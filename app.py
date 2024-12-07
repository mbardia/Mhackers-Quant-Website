from flask import Flask, render_template, request, url_for
from bollinger_bands import bollinger_bands
from MACD import MACDStrategy
from SMAcrossover import SMACrossover
from EMA import EMACrossover

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    stock = request.form["stock"]
    start_date = request.form["start-date"]
    end_date = request.form["end-date"]

    # Bollinger Bands
    bb_image_path, bb_error = bollinger_bands(stock, start_date, end_date)
    if bb_error:
        return f"<h1>Error in Bollinger Bands: {bb_error}</h1><a href='/'>Go back</a>"

    # MACD Strategy
    macd_strategy = MACDStrategy(stock, start_date, end_date)
    macd_image_path, macd_error = macd_strategy.plot_results()
    macd_signals = macd_strategy.print_signals()
    if macd_error:
        return f"<h1>Error in MACD: {macd_error}</h1><a href='/'>Go back</a>"

    
    #SMA strategy
    sma_strategy = SMACrossover(stock,start_date,end_date,20,50)
    sma_image_path, sma_error = sma_strategy.plot_results()
    if sma_error:
        return f"<h1>Error in SMA: {sma_error}</h1><a href='/'>Go back</a>"
    
    #EMA startegy
    ema_strategy = EMACrossover(stock,start_date,end_date,20,50)
    ema_image_path, ema_error = ema_strategy.plot_results()
    if ema_error:
        return f"<h1>Error in EMA: {ema_error}</h1><a href='/'>Go back</a>"

    # Combine Results and Return
    return f"""
    <h1>Stock Analysis for {stock}</h1>
    <h2>Bollinger Bands</h2>
    <img src="{url_for('static', filename=bb_image_path.split('/')[-1])}" alt="Bollinger Bands">
    <h2>MACD Strategy</h2>
    <img src="{url_for('static', filename=macd_image_path.split('/')[-1])}" alt="MACD Strategy">
    <h2>SMA Crossover Strategy</h2>
    <img src="{url_for('static', filename=sma_image_path.split('/')[-1])}" alt="SMA Strategy">
    <h2>EMA Crossover Strategy</h2>
    <img src="{url_for('static', filename=ema_image_path.split('/')[-1])}" alt="EMA Strategy">
    <br>
    <a href="/">Go back</a>
     """
    

if __name__ == "__main__":
    app.run(debug=True)

