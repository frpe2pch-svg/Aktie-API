from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import time

app = Flask(__name__)
CORS(app)

@app.route("/portfolio")
def portfolio():
    tickers_param = request.args.get("tickers", "")
    tickers = [t.strip().upper() for t in tickers_param.split(",") if t.strip()]

    if not tickers:
        return jsonify({"error": "Ingen ticker angiven. Lovable måste skicka tickers."})

    stocks = []

    for t in tickers:
        print(f"Hämtar data för: {t}")
        try:
            ticker_obj = yf.Ticker(t)

            # Historiska priser
            df = ticker_obj.history(period="1mo", interval="1d")
            latest_price = round(float(df["Close"].iloc[-1]), 2) if not df.empty else None
            ma20 = round(df["Close"].rolling(window=20).mean().iloc[-1], 2) if len(df) >= 20 else None
            volatility = round(df["Close"].pct_change().std(), 4) if not df.empty else None

            # Försök med fast_info (snabbare och stabilare)
            info = {}
            try:
                info = ticker_obj.fast_info
            except Exception:
                pass

            # Fallback till "info" om fast_info inte ger tillräckligt
            if not info or "market_cap" not in info:
                try:
                    info = ticker_obj.info
                except Exception:
                    info = {}

            stocks.append({
                "symbol": t,
                "name": info.get("shortName") or info.get("longName") or t,
                "current_price_usd": latest_price or info.get("last_price"),
                "ma20": ma20,
                "volatility": volatility,
                "beta": info.get("beta"),
                "pe_ratio": info.get("trailingPE") or info.get("peRatio"),
                "eps": info.get("trailingEps") or info.get("eps"),
                "dividend_yield": info.get("dividendYield"),
                "market_cap": info.get("marketCap") or info.get("market_cap"),
                "sector": info.get("sector") or info.get("industry") or "Okänd",
                "motivation": "",
                "recommended_amount": None
            })

            # Liten paus för att undvika rate limit
            time.sleep(0.5)

        except Exception as e:
            print(f"Fel för {t}: {e}")
            stocks.append({
                "symbol": t,
                "name": t,
                "current_price_usd": None,
                "ma20": None,
                "volatility": None,
                "beta": None,
                "pe_ratio": None,
                "eps": None,
                "dividend_yield": None,
                "market_cap": None,
                "sector": None,
                "motivation": "",
                "recommended_amount": None
            })

    return jsonify({"stocks": stocks})

@app.route("/")
def home():
    return jsonify({"message": "Servern fungerar! Prova /portfolio?tickers=AAPL,TSLA"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
