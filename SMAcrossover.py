import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

class SMACrossover:
    def __init__(self, ticker, start_date, end_date, short_window=20, long_window=50):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.short_window = short_window
        self.long_window = long_window
        self.data = None
        self.data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        self.calculate_sma()
        self.generate_signals()

    def calculate_sma(self):
        data_length = len(self.data)

        if data_length >= self.short_window:
            self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        else:
            print(
                f"Data range is smaller than the short SMA window ({self.short_window} days). Adjusting the window size.")
            self.data['SMA_Short'] = self.data['Close'].rolling(window=data_length).mean()

        if data_length >= self.long_window:
            self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        else:
            print(
                f"Data range is smaller than the long SMA window ({self.long_window} days). Adjusting the window size.")
            self.data['SMA_Long'] = self.data['Close'].rolling(window=data_length).mean()

    def generate_signals(self):
        self.data['Signal'] = 0.0
        self.data['Signal'] = np.where(self.data['SMA_Short'] > self.data['SMA_Long'], 1.0, 0.0)
        self.data['Crossover'] = self.data['Signal'].diff()

    def plot_results(self):
        plt.figure(figsize=(16, 9))
        plt.plot(self.data['Close'], label='Close Price', color='blue', lw=2.5, zorder=1)
        plt.plot(self.data['SMA_Short'], label=f'{self.short_window}-Day SMA', color='green', lw=1.5, linestyle='--',
                 zorder=2)
        plt.plot(self.data['SMA_Long'], label=f'{self.long_window}-Day SMA', color='red', lw=1.5, linestyle='--',
                 zorder=2)

        plt.scatter(self.data[self.data['Crossover'] == 1.0].index,
                    self.data['Close'][self.data['Crossover'] == 1.0] * 1.01,  # offset slightly above the line
                    marker='^', color='green', s=100, label='Buy Signal', zorder=3)

        plt.scatter(self.data[self.data['Crossover'] == -1.0].index,
                    self.data['Close'][self.data['Crossover'] == -1.0] * 0.99,  # offset slightly below the line
                    marker='v', color='red', s=100, label='Sell Signal', zorder=3)

        plt.title(f'{self.ticker} SMA Crossover Strategy', fontsize=16)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Price ($)', fontsize=14)
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.legend(loc='upper left', fontsize=12, frameon=True, shadow=True)
        plt.tight_layout()
        plt.show()
        image_path = f"static/{self.ticker}_{self.start_date}_{self.end_date}_SMA.png"
        plt.savefig(image_path)
        plt.close()
        return image_path, None

if __name__ == "__main__":
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Simple Moving Average Crossover Strategy")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    parser.add_argument("--short_window", type=int, default=20, help="Short moving average window (default: 20)")
    parser.add_argument("--long_window", type=int, default=50, help="Long moving average window (default: 50)")

    # Parse arguments
    args = parser.parse_args()

    # Instantiate and run the strategy
    sma_strategy = SMACrossover(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        short_window=args.short_window,
        long_window=args.long_window
    )
    sma_strategy.plot_results()