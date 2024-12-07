import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse

def bollinger_bands(ticker, start_date, end_date, period=20, k=2):

   extended_start_date = ( datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=period + 10)).strftime('%Y-%m-%d')
   data = yf.download(ticker, start=extended_start_date, end=end_date, interval="1d", progress=False)


   if data.empty:
        print("No data found for the given ticker or date range.")
        return

    
   data['SMA'] = data['Close'].rolling(window=period).mean()
   data['STD'] = data['Close'].rolling(window=period).std()
   data['Upper Band'] = data['SMA'] + (k * data['STD'])
   data['Lower Band'] = data['SMA'] - (k * data['STD'])

    
   data = data.loc[start_date:]

   if data.empty:
        print("No valid data after filtering for the requested date range.")
        return

   
   plt.figure(figsize=(14, 7))
   plt.plot(data.index, data['Close'], label=f'{ticker} Closing Price', color='blue')
   plt.plot(data.index, data['SMA'], label=f'{period}-Day SMA', color='orange', linestyle='--')
   plt.plot(data.index, data['Upper Band'], label=f'Upper Band (+{k} SD)', color='green', linestyle='--')
   plt.plot(data.index, data['Lower Band'], label=f'Lower Band (-{k} SD)', color='red', linestyle='--')
   plt.fill_between(data.index, data['Lower Band'], data['Upper Band'], color='gray', alpha=0.2)
   plt.title(f"Bollinger Bands for {ticker} ({start_date} to {end_date})")
   plt.xlabel("Date")
   plt.ylabel("Price")
   plt.legend(loc="upper left")
   plt.grid()
   #plt.show()
   image_path = f"static/{ticker}_{start_date}_{end_date}_bollinger.png"
   plt.savefig(image_path)
   plt.close()
   return image_path, None


def main():
    parser = argparse.ArgumentParser(description="Calculate and plot Bollinger Bands for a stock.")
    parser.add_argument("ticker", type=str, help="The stock ticker symbol (e.g., AAPL, MSFT).")
    parser.add_argument("start_date", type=str, help="Start date for historical data (YYYY-MM-DD).")
    parser.add_argument("end_date", type=str, help="End date for historical data (YYYY-MM-DD).")
    parser.add_argument("--period", type=int, default=20, help="Lookback period for the SMA (default: 20).")
    parser.add_argument("--k", type=float, default=2, help="Multiplier for standard deviation (default: 2).")
    args = parser.parse_args()
    bollinger_bands(args.ticker, args.start_date, args.end_date, args.period, args.k)

if __name__ == "__main__":
    main()
