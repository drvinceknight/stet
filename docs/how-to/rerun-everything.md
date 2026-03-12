# Re-run Everything

To clear the store and re-run all experiments from scratch:

```python
stet.reset()
# [stet] Clear all records in _stet_store.csv? [y/N] y
```

In non-interactive environments (CI, scripts) the prompt is skipped and the store is
cleared immediately.
