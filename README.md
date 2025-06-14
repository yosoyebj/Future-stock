# Future-stock

This project contains small utilities for downloading Indian stock data and
running basic prediction models.  Historical data is fetched with
`fetch_data.py` and stored under `future stock/csv/`.  The script
`enhanced_stock_predictor.py` demonstrates feature engineering and simple
linear regression to estimate the next closing price.

## Requirements

The prediction script relies on several third‑party libraries.  Install them
with `pip` before running any of the tools:

```bash
pip install pandas numpy scikit-learn newsapi-python newspaper3k textblob
```

If you also need to fetch new stock data, install `yfinance`:

```bash
pip install yfinance
```

## Basic usage

1. Run `future stock/fetch_data.py` to download the CSV files.  They will be
   saved in `future stock/csv/`.
2. Execute `python enhanced_stock_predictor.py` from the repository root and
   select one of the downloaded stock symbols when prompted.

`enhanced_stock_predictor.py` loads the saved CSV files directly so it works
independently of the other scripts once the data is in place.
