from flask import Flask, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

@app.route("/portfolio")
def portfolio():
    tickers = ["AAPL", "MSFT", "GOOG"]
    data = {}
    for t in tickers:
        try:
            df = yf.download(t, period="1mo", interval="1wk", progress=False, threads=False, auto_adjust=False)
            if not df.empty:
                data[t] = round(float(df["Close"].iloc[-1]), 2)
            else:
                data[t] = None
        except:
            data[t] = None
    return jsonify(data)

@app.route("/")
def home():
    return jsonify({"message": "Servern fungerar! Prova /portfolio"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
