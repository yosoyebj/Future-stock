import pandas as pd
from fetch_data import stocks
import os
import sys
import time
from loading_anime import loading_animation
import numpy as np
import threading
from newsapi import NewsApiClient
from newspaper import Article
from textblob import TextBlob

import matplotlib.pyplot as plt

def read_csv():

    try:

        print(list(stocks.keys()))
        name=input("\n what company you want to work on?: \n")
        file_name = f'csv/{name}.csv'
        data = pd.read_csv(file_name, skiprows=1)# made the header as the first raw, the TCS.NS part will consider as header. or when analyze data they will analyze it
        data.columns = ["Close","high","Low","open","Volume"]
        loading_animation() #just fpr the funny loading animation
        print(f" \nsuccess fully read the csv :{name}")
        time.sleep(1)

        
        return data,name
        
        
        
    except Exception as e:
        print("oooops, you have entered the wrong name please check the spelling\n")
        read_csv()

data,name = read_csv() #calling read csv

# function for inspect
def inspect_data(data_ins):
    print(data_ins.head())
    # checking missing values
    print("\nMissing values per column:\n", data_ins.isnull().sum())
    print("\n Data types :\n", data_ins.dtypes)
    for col in data.columns:
        print(f"\n📌 Non-numeric values in '{col}':")
        print(data[pd.to_numeric(data[col], errors='coerce').isna()][col].unique())




def feature_engineering(data,name):
    def ema_sma(data):
    #computing the 50 day and 200 day simple moving averages
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200']= data['Close'].rolling(window=200).mean()


        #20 day and 50 day ema (short term trend calculating)
        data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

        # plot it in a graph

        plt.figure(figsize=(12,6))

        #plot closing price
        plt.plot(data['Close'], label = "stock price", color='blue', alpha =0.6)

        #plot sma line
        plt.plot(data['SMA_50'], label="50-day sma", linestyle="dashed", color='red')
        plt.plot(data['SMA_200'], label="200-day sma", linestyle="dashed", color='green')

        #plot ema line
        plt.plot(data['EMA_20'], label="20-day ema", linestyle="dotted", color='purple')
        plt.plot(data['EMA_50'], label="50-day ema", linestyle="dotted", color='orange')

        #add title and legend
        plt.title("stock price with SMA and EMA")
        plt.legend()
        
        plt.show()

    #write a function for rsi

    def rsi(data, period=14):
        print("\033[1,31mRSI is calculated\033[0m")
        delta = data["Close"].diff(1) #get the daily price change, getting difference of close price for ex, yesterday and today
        gain = np.where(delta>0, delta, 0) # keep only positive gaines
        loss = np.where(delta<0, abs(delta), 0) # keep only negetive loses
        
        avg_gain= pd.Series(gain).rolling(window=period).mean()
        avg_loss= pd.Series(loss).rolling(window=period).mean()

        rs =avg_gain /avg_loss
        #compute RSI using standard formula

        rsi = 100 - (100/(1+rs))
        data["RSI"]= rsi #added rsi to datframe
        print("check the rsi values here")
        print(data.head(30))

    def macd(data):
        data["EMA_12"] = data["Close"].ewm(span=12, adjust=False).mean() #12 days ema
        data["EMA_26"] = data["Close"].ewm(span=26, adjust=False).mean() #26 days ema
        data["MACD"]   = data["EMA_12"]-data["EMA_26"] #macd
        data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean() #signal line
        data["MACD_Histogram"]= data["MACD"]-data["Signal_Line"]
        
        #plotting
        plt.figure(figsize=(12,6))
        #plot MACD Line
        plt.plot(data.index, data["MACD"], label="MACD Line", color="blue" )
        plt.plot(data.index, data["Signal_Line"], label="Signal_line", color="red")
        #plotting the MACD Histogram
        plt.bar(data.index, data["MACD_Histogram"], label="Histogram", color ="grey", alpha=0.5)
        #adding zero line for refernce
        plt.axhline(0, color="black", linewidth=1, linestyle="dashed")
        #adding legend to display label name 
        plt.legend()
        plt.title("MACD_indicator")
        
        plt.show()
    
    def vma(data):
        data["VMA_50"] =data["Volume"].rolling(window=50).mean() #50-day vma
        data["VMA_10"] =data["Volume"].rolling(window=50).mean() #10-day VMA

        #calculating on-balance volume(OBV)
        data["Daily_change"] = data["Close"].diff()
        data["OBV"] =(data["Volume"] * data["Daily_change"].apply(lambda x: 1 if x> 0 else (-1 if x<0 else 0))).cumsum()

        #calcukatre volume price trend
        data["VPI"]= ((data["Close"].diff()/data["Close"].shift(1))
                      * data["Volume"]).cumsum()
        
        #plot volume trend indicators
        plt.figure(figsize=(12,6))

        #plot volume moving average
        plt.subplot(3,1,1)
        plt.plot(data.index, data["Volume"], label="Volume", color="gray", alpha=0.6)
        plt.plot(data.index, data["VMA_50"], label="50-day VMA", color="blue", linewidth=2.5)
        plt.plot(data.index, data["VMA_10"], label="10_day VMA", color="red")
        plt.title("Volume Moving Averages")
        plt.legend()

        #plot OBV
        plt.subplot(3,1,2)
        plt.plot(data.index, data["OBV"], label="On-balance Volume(OBV)",color="purple")
        plt.title("On-Balance Volume (OBV)")
        plt.legend()
        #Plot VPT

        plt.subplot(3,1,3)
        plt.plot(data.index, data["VPI"], label="Volume Price Trend (VPT)", color="green")
        plt.title("Volume price trend (VPT)")
        plt.legend()

        plt.tight_layout()
        plt.show()
    

    def historical_price_difference(data, periods=[1,3,5,10] ):
        for period in periods:
            col_name= f"price_change_{period}D"
            data[col_name]= data["Close"]- data["Close"].shift(period)
        print("historical pricechanges /n")
        print(data)

    
  #  newsapi = NewsApiClient(api_key='dad7397d398a496e9a1d341c9eaf7fcc')




    def sentiment_analysys(name):
        #search for recent news about the company
        newsapi = NewsApiClient(api_key='dad7397d398a496e9a1d341c9eaf7fcc')

        response = newsapi.get_everything(
            q=name, #keyword to search
            sort_by='relevancy',
            language='en',
            page_size=20
        )
        #extract article URLs
        urls = [article['url'] for article in response['articles']]

        #download article using newspaper 3k

        texts=[]

        for url in urls:
            try:
                article= Article(url)
                article.download()
                article.parse()
                texts.append(article.text)
            except Exception as e: #some url that has ads or something else might fail
                print(f"failed t process {url}: {e}")

        sentiment_scores = [] # getting sentiment score

        for text in texts:
            score= TextBlob(text).sentiment.polarity
            sentiment_scores.append(score)
        
        #computing avg sentiment score

        if sentiment_scores:
            avg_sentiment =sum(sentiment_scores)/ len(sentiment_scores)
        else:
            avg_sentiment=0 #default if no valid articles

        #output
        print(f"\n Average sentiment scores for news :{avg_sentiment:.2f}")

        if avg_sentiment > 0.3:
            print("positive, potential bullish")
        elif avg_sentiment < -0.3:
            print("market sentiment is negetive -be careful")
        else:
            print("market sentiment is nuetral")





    


        


   

    #ema_sma(data)
    #rsi(data)

    #threading is used to run functions at the same time
    t1= threading.Thread(target=ema_sma(data))
    t2= threading.Thread(target=rsi(data))
    t3= threading.Thread(target=macd(data))
    t4= threading.Thread(target= vma(data))
    t5=threading.Thread(target=historical_price_difference(data))
    t6=threading.Thread(target=sentiment_analysys(name,))


    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    






inspect_data(data)
feature_engineering(data,name)


