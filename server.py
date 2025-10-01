from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd

app = Flask(__name__)

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

            # Historiska priser senaste 1 månad
            df = ticker_obj.history(period="1mo", interval="1d")
            latest_price = round(float(df["Close"].iloc[-1]), 2) if not df.empty else None
            ma20 = round(df["Close"].rolling(window=20).mean().iloc[-1], 2) if len(df) >= 20 else None
            volatility = round(df["Close"].pct_change().std(), 4) if not df.empty else None

            # Fundamental data
            info = ticker_obj.info
            name = info.get("shortName") or t
            pe_ratio = info.get("trailingPE")
            eps = info.get("trailingEps")
            dividend_yield = info.get("dividendYield")
            market_cap = info.get("marketCap")
            sector = info.get("sector")
            beta = info.get("beta")

            stocks.append({
                "symbol": t,
                "name": name,
                "current_price_usd": latest_price,
                "ma20": ma20,
                "volatility": volatility,
                "beta": beta,
                "pe_ratio": pe_ratio,
                "eps": eps,
                "dividend_yield": dividend_yield,
                "market_cap": market_cap,
                "sector": sector,
                "motivation": "",
                "recommended_amount": None
            })

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
