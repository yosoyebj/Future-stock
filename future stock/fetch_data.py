import yfinance as yf
import os


stocks = {
    "TCS": "TCS.NS",
    "DLF": "DLF.NS",
    "LIC": "LICI.NS",
    "MAHINDRA": "M&M.NS",
    "MARUTI": "MARUTI.NS",
    "RELIANCE": "RELIANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATAPOWER": "TATAPOWER.NS",
    "ZOMATO": "ZOMATO.NS"
    
    
}
if __name__ == "__main__":

    # downloading historical data
    data = {name: yf.download(ticker, start='2015-01-01', end='2024-12-31') for name, ticker in stocks.items()}

    #print head
    for name, df in data.items():
        print(f"head of {name}:\n", df.head(), "\n")


    #save data to csv
    #make a folder called csv to store csv file there
    os.makedirs('csv', exist_ok =True)

    for name, df in data.items():
        file_path = f'csv/{name}.csv'
        df.to_csv(file_path, index=False) #saved 
        print(f"saved {name}.csv successfully")



