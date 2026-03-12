# How `stet` relates to similar libraries

Several Python libraries solve adjacent problems to `stet`. Understanding how they
differ clarifies what `stet` is for and why it makes the design choices it does.

## `joblib.Memory`

`joblib.Memory` is the most widely used tool in this space. It wraps a function so that
the return value is persisted to disk on the first call and returned from the cache on
subsequent identical calls: standard memoization, made durable across processes and
restarts.

Because `joblib.Memory` stores return values, its storage is opaque: results live as
pickle files in a nested directory structure not meant to be read by anything other than
`joblib` itself. There is no way to open the cache in a spreadsheet, query it with SQL,
or inspect it with standard tools. It also stores everything the function returns, which
can mean large files for functions that return arrays or models.

It also has no concept of a key subset. The cache key is the full set of arguments;
there is no way to say "these parameters define the experiment identity, but this one is
just a computational setting". For research workflows where you want to vary convergence
tolerances or iteration counts without invalidating cached results, this is a
significant constraint.

`stet` is not trying to replace `joblib.Memory`; it is solving a different problem.

## `checkpointing`

The `checkpointing` package (PyPI) is a decorator that caches return values as pickle
files and skips re-execution for identical arguments, with configurable behaviour on
errors. Its intent and API are close to `joblib.Memory`: persist outputs, skip
re-computation.

The same differences apply. Storage is not human-readable or queryable, return values
are always persisted, and there is no user-defined key subset. It adds some useful
error-handling flexibility that `joblib.Memory` lacks, but the underlying model - cache
the output, look it up on re-call - is the same.

## `checkpointer`

`checkpointer` (PyPI) is a more sophisticated decorator focused on *cache correctness*.
It can detect when the decorated function's source code or dependencies have changed and
invalidate the cache accordingly. It also supports async functions and robust hashing of
complex objects such as NumPy arrays and PyTorch tensors.

This solves a different problem. The question `checkpointer` answers is: *is this cached
result still valid given that the code may have changed?* The question `stet` answers
is: *has this parameter combination been run before?* For a researcher running a fixed
parameter sweep across sessions, code-aware invalidation is not needed, and the overhead
of hashing complex objects would add cost to every call.

## `memento` (wickerlab)

`memento` is the closest in intent to `stet`. It is explicitly designed for researchers
running expensive experiments over a parameter grid, with built-in parallelisation and
result caching.

The key difference is that `memento` is workflow-prescriptive. You define your parameter
grid upfront as a configuration object and pass it to `Memento.run()`, which handles
iteration and parallelisation. This requires structuring your experiment around
`memento`'s API.

`stet` takes the opposite position: it is workflow-neutral. You decorate your function
and loop over parameters however you already do: a `for` loop, a list comprehension, a
call from a notebook cell, a parallel map. The decorator fits into existing code without
restructuring it, and composes with whatever parallelisation approach you already use.
