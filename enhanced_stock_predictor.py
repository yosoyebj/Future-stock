import os
import pandas as pd
import numpy as np
from newsapi import NewsApiClient
from newspaper import Article
from textblob import TextBlob
from sklearn.linear_model import LinearRegression
import datetime

DATA_DIR = 'future stock/csv'


def load_stock(name: str) -> pd.DataFrame:
    """Load CSV for given stock symbol."""
    path = os.path.join(DATA_DIR, f"{name}.csv")
    df = pd.read_csv(path, skiprows=2, names=["Close", "High", "Low", "Open", "Volume"])
    return df.astype(float)


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicator columns to DataFrame."""
    df = df.copy()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

    df['VMA_50'] = df['Volume'].rolling(window=50).mean()
    df['VMA_10'] = df['Volume'].rolling(window=10).mean()

    df['Daily_change'] = df['Close'].diff()
    df['OBV'] = (df['Volume'] * np.sign(df['Daily_change'].fillna(0))).cumsum()
    df['VPI'] = ((df['Close'].pct_change()) * df['Volume']).cumsum()

    for period in [1, 3, 5, 10]:
        df[f'price_change_{period}D'] = df['Close'] - df['Close'].shift(period)

    return df


def fetch_sentiment(keyword: str) -> float:
    """Return average sentiment score using NewsAPI and TextBlob."""
    try:
        newsapi = NewsApiClient(api_key='dad7397d398a496e9a1d341c9eaf7fcc')
        response = newsapi.get_everything(q=keyword, sort_by='relevancy', language='en', page_size=20)
        urls = [article['url'] for article in response['articles']]
        texts = []
        for url in urls:
            try:
                article = Article(url)
                article.download()
                article.parse()
                texts.append(article.text)
            except Exception:
                continue
        scores = [TextBlob(t).sentiment.polarity for t in texts]
        return sum(scores) / len(scores) if scores else 0.0
    except Exception:
        return 0.0


def prepare_dataset(name: str):
    df = load_stock(name)
    df = compute_features(df)
    df['sentiment'] = fetch_sentiment(name)
    df['target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)
    X = df.drop('target', axis=1)
    y = df['target']
    return X, y, df


def display_features(df: pd.DataFrame, rows: int = 5) -> None:
    """Print available features and show a sample of the engineered data."""
    features = df.drop('target', axis=1)
    print("\nFeature columns:")
    print(", ".join(features.columns))
    print("\nSample after feature engineering:")
    print(features.head(rows))


def train_model(X: pd.DataFrame, y: pd.Series) -> LinearRegression:
    model = LinearRegression()
    model.fit(X, y)
    return model


START_DATE = datetime.date(2015, 1, 1)


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
    delta = datetime.timedelta(days=1)
    cur = START_DATE
    idx = 0
    while cur < date:
        if cur.weekday() < 5:
            idx += 1
        cur += delta
    if cur == date and cur.weekday() < 5:
        return idx
    while cur.weekday() >= 5:
        cur -= delta
    return idx if cur < date else idx - 1


def main():
    print("Available CSV files:")
    for file in os.listdir(DATA_DIR):
        if file.endswith('.csv'):
            print('-', file[:-4])

    name = input("Enter stock symbol: ").strip().upper()
    try:
        X, y, df = prepare_dataset(name)
    except FileNotFoundError:
        print("CSV for given symbol not found.")
        return

    display_features(df)

    model = train_model(X, y)
    latest_features = df.drop('target', axis=1).iloc[-1:]
    prediction = model.predict(latest_features)[0]
    print(f"Predicted next closing price for {name}: {prediction:.2f}")

    # Train simple time-based regression and predict for user-specified date
    prices = df['Close'].tolist()
    a, b = train_linear_regression(prices)

    date_str = input("Enter future date (YYYY-MM-DD): ")
    try:
        future_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format")
        return

    idx = trading_day_index(future_date)
    date_pred = predict_price(a, b, idx)
    print(f"Predicted closing price for {name} on {future_date}: {date_pred:.2f}")


if __name__ == '__main__':
    main()
