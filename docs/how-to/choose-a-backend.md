# Choose a Backend

`stet` supports four storage backends. The backend is selected automatically from the file extension you pass to `store=`.

## CSV (`.csv`)

The default. Human-readable, easy to inspect in a spreadsheet.

```python
@stet.once(store='_stet_store.csv')
def run(alpha, beta): ...
```

**Use when:** You want to inspect or edit records manually, or share the store with non-Python tools.

## JSON (`.json`)

Pure Python, no extra dependencies beyond `filelock`.

```python
@stet.once(store='_stet_store.json')
def run(alpha, beta): ...
```

**Use when:** You want a dependency-free, human-readable format.

## SQLite (`.sqlite`)

Robust, concurrent-friendly, query-able with standard SQL tools.

```python
@stet.once(store='_stet_store.sqlite')
def run(alpha, beta): ...
```

**Use when:** You have many thousands of records, need fast lookups, or want to query the store with SQL.

## Parquet (`.parquet`)

Requires `stet[parquet]`. Compact binary format, fast for large datasets.

```
$ uv add stet[parquet]
```

or

```
$ python -m pip install stet[parquet]
```

```python
@stet.once(store='_stet_store.parquet')
def run(alpha, beta): ...
```

**Use when:** You have very large stores and want the smallest file size with fast reads.

## Comparison

| Format  | Inspect with             | Extra install  | Fast for large stores |
|---------|--------------------------|----------------|-----------------------|
| CSV     | Any text editor          | —              | No                    |
| JSON    | Any text editor          | —              | No                    |
| SQLite  | DB browser / sqlite3 CLI | —              | Yes                   |
| Parquet | pandas / DuckDB          | `stet[parquet]` | Yes                  |
