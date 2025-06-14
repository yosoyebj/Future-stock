import csv
import datetime
import math

DATA_DIR = 'future stock/csv'
START_DATE = datetime.date(2015, 1, 1)

stocks = {
    'TCS': 'TCS.csv',
    'DLF': 'DLF.csv',
    'LIC': 'LIC.csv',
    'MAHINDRA': 'MAHINDRA.csv',
    'MARUTI': 'MARUTI.csv',
    'RELIANCE': 'RELIANCE.csv',
    'SUNPHARMA': 'SUNPHARMA.csv',
    'TATAPOWER': 'TATAPOWER.csv',
    'ZOMATO': 'ZOMATO.csv',
}

def load_close_prices(filename):
    path = f"{DATA_DIR}/{filename}"
    close_prices = []
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        # skip header and ticker row
        for row in rows[2:]:
            if row:
                close_prices.append(float(row[0]))
    return close_prices


def train_linear_regression(data):
    n = len(data)
    x_vals = list(range(n))
    mean_x = sum(x_vals) / n
    mean_y = sum(data) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, data))
    denominator = sum((x - mean_x) ** 2 for x in x_vals)
    b = numerator / denominator if denominator else 0
    a = mean_y - b * mean_x
    return a, b


def predict_price(a, b, index):
    return a + b * index


def trading_day_index(date):
    # compute trading day index relative to START_DATE skipping weekends
    delta = datetime.timedelta(days=1)
    cur = START_DATE
    idx = 0
    while cur < date:
        if cur.weekday() < 5:
            idx += 1
        cur += delta
    if cur == date and cur.weekday() < 5:
        return idx
    # if date is weekend, move to previous trading day
    while cur.weekday() >= 5:
        cur -= delta
    return idx if cur < date else idx - 1


def main():
    print("Available stocks:")
    for key in stocks:
        print(f"- {key}")
    name = input("\nEnter stock symbol from above: ").strip().upper()
    filename = stocks.get(name)
    if not filename:
        print("Unknown stock symbol")
        return

    prices = load_close_prices(filename)
    if not prices:
        print("No data found")
        return

    print(f"Loaded {len(prices)} records for {name}.")
    print("First 5 closing prices:", prices[:5])

    split_idx = int(len(prices) * 0.8)
    train_data = prices[:split_idx]
    a, b = train_linear_regression(train_data)
    print("Model trained using linear regression.")

    date_str = input("Enter future date (YYYY-MM-DD): ")
    try:
        future_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format")
        return

    idx = trading_day_index(future_date)
    pred = predict_price(a, b, idx)
    print(f"Predicted closing price for {name} on {future_date}: {pred:.2f}")

if __name__ == '__main__':
    main()
