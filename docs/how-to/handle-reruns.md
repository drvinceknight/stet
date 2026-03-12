# Re-run a Specific Experiment

If an experiment produced bad results and you want to redo it, remove it from the store:

```python
stet.reset(key_dict={'alpha': '0.1', 'seed': '42'})
```

Note that values are stored as strings, so pass string values to `key_dict`. Then call
the function again; `stet` will no longer find it in the store and will execute
normally.
