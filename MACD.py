import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import argparse

class MACDStrategy:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.download_data()
        self.calculate_macd()
        self.generate_signals()

    def download_data(self):
        """Download historical data."""
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date, progress=False)
        data.reset_index(inplace=True)  # Ensure dates are in a column, not the index
        return data

    def calculate_macd(self):
        """Calculate the MACD and signal line."""
        # Calculate MACD line
        self.data['MACD'] = self.data['Close'].ewm(span=12, adjust=False).mean() - self.data['Close'].ewm(span=26, adjust=False).mean()
        # Calculate signal line
        self.data['MACD_SIGNAL'] = self.data['MACD'].ewm(span=9, adjust=False).mean()

    def generate_signals(self):
        """Generate buy and sell signals with more robust conditions."""
        # Create Buy and Sell columns
        self.data['Buy_Signal'] = False
        self.data['Sell_Signal'] = False

        # More sophisticated signal generation
        for i in range(1, len(self.data)):
            # Buy signal: MACD crosses above signal line and is negative (potential trend reversal)
            if (self.data['MACD'].iloc[i] > self.data['MACD_SIGNAL'].iloc[i] and 
                self.data['MACD'].iloc[i-1] <= self.data['MACD_SIGNAL'].iloc[i-1] and 
                self.data['MACD'].iloc[i] < 0):
                self.data.loc[self.data.index[i], 'Buy_Signal'] = True

            # Sell signal: MACD crosses below signal line and is positive (potential trend reversal)
            if (self.data['MACD'].iloc[i] < self.data['MACD_SIGNAL'].iloc[i] and 
                self.data['MACD'].iloc[i-1] >= self.data['MACD_SIGNAL'].iloc[i-1] and 
                self.data['MACD'].iloc[i] > 0):
                self.data.loc[self.data.index[i], 'Sell_Signal'] = True

    def print_signals(self):
     if self.data is None:
        print("No data available.")
        return

    # Ensure 'Date' is available as a column
     if 'Date' not in self.data.columns:
        self.data = self.data.reset_index()  # Reset index to make 'Date' a column

     # Buy signals
     buy_signals = self.data[self.data['Buy_Signal']]
     print("\n--- BUY SIGNALS ---")
     for _, row in buy_signals.iterrows():
        date = row['Date'].strftime('%Y-%m-%d') if isinstance(row['Date'], pd.Timestamp) else str(row['Date'])
        price = float(row['Close'])  # Ensure price is a scalar
        print(f"Date: {date}, Price: ${price:.2f}")

     # Sell signals
     sell_signals = self.data[self.data['Sell_Signal']]
     print("\n--- SELL SIGNALS ---")
     for _, row in sell_signals.iterrows():
        date = row['Date'].strftime('%Y-%m-%d') if isinstance(row['Date'], pd.Timestamp) else str(row['Date'])
        price = float(row['Close'])  # Ensure price is a scalar
        print(f"Date: {date}, Price: ${price:.2f}")


    def plot_results(self):
        """Plot the MACD strategy results with improved signal visualization."""
        # Create two subplots with explicit heights
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]}, 
                                        sharex=True)
        
        # Price subplot
        ax1.plot(self.data['Date'], self.data['Close'], label='Close Price', color='blue', lw=2)
        
        # Buy signals on price chart
        buy_signals = self.data[self.data['Buy_Signal']]
        ax1.scatter(buy_signals['Date'], buy_signals['Close'], color='green', marker='^', s=200, 
                    label='Buy Signal', zorder=5, edgecolors='black', linewidth=1)
        
        # Sell signals on price chart
        sell_signals = self.data[self.data['Sell_Signal']]
        ax1.scatter(sell_signals['Date'], sell_signals['Close'], color='red', marker='v', s=200, 
                    label='Sell Signal', zorder=5, edgecolors='black', linewidth=1)
        
        ax1.set_title(f'{self.ticker} MACD Strategy', fontsize=16)
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(alpha=0.7, linestyle='--')

        # MACD subplot
        ax2.plot(self.data['Date'], self.data['MACD'], label='MACD', color='purple', lw=1.5)
        ax2.plot(self.data['Date'], self.data['MACD_SIGNAL'], label='Signal Line', color='orange', lw=1.5, linestyle='--')
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('MACD', fontsize=12)
        ax2.legend(loc='best')
        ax2.grid(alpha=0.7, linestyle='--')

        # Format x-axis
        date_format = mpl_dates.DateFormatter('%d %b %Y')
        ax1.xaxis.set_major_formatter(date_format)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.show()
        image_path = f"static/{self.ticker}_{self.start_date}_{self.end_date}_MACD.png"
        plt.savefig(image_path)
        plt.close()
        return image_path, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MACD strategy for a given stock ticker.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    macd_strategy = MACDStrategy(ticker=args.ticker, start_date=args.start_date, end_date=args.end_date)
    macd_strategy.plot_results()
    macd_strategy.print_signals()

