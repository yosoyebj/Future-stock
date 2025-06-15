# Future-stock

This project contains small utilities for downloading Indian stock data and
running basic prediction models.  Historical data is fetched with
`fetch_data.py` and stored under `future stock/csv/`.  The script
`enhanced_stock_predictor.py` demonstrates feature engineering and uses those
features together with news sentiment in a linear regression model to estimate
the next closing price.  The script prints the most recent engineered feature
rows before showing the prediction.

## Requirements

The prediction script relies on several third‑party libraries.  Install them
using the provided requirements file before running any of the tools:

```bash
pip install -r requirements.txt
```

This file includes all libraries needed by `enhanced_stock_predictor.py` as
well as `yfinance` for downloading new datasets.

## Basic usage

1. Run `future stock/fetch_data.py` to download the CSV files.  They will be
   saved in `future stock/csv/`.
2. Execute `python enhanced_stock_predictor.py` from the repository root and
   select one of the downloaded stock symbols when prompted.

`enhanced_stock_predictor.py` loads the saved CSV files directly so it works
independently of the other scripts once the data is in place.
