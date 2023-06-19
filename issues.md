# Known issues

- Giving error when selecting time resolution to *monthly* if the date range is less than a month (e.g., 2023-06-01 to 2023-06-18).
    ```
    File "callbacks.py", line 137, in update_figure
        numdays = (df_updated.index.max() - df_updated.index.min()).days
    AttributeError: 'float' object has no attribute 'days'
    ```
