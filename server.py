from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route("/portfolio")
def portfolio():
    # Hämta tickers från query-parameter
    tickers_param = request.args.get("tickers", "")
    tickers = [t.strip().upper() for t in tickers_param.split(",") if t.strip()]

    if not tickers:
        return jsonify({"error": "Ange minst en ticker, t.ex. ?tickers=AAPL,TSLA"})

    stocks = []

    for t in tickers:
        try:
            # Hämta veckodata
            df = yf.download(t, period="1mo", interval="1wk", progress=False, threads=False, auto_adjust=False)
            price = round(float(df["Close"].iloc[-1]), 2) if not df.empty else None

            # Hämta företagsinfo från Yahoo Finance
            info = yf.Ticker(t).info
            name = info.get("shortName") or t  # fallback till ticker om namn saknas

            stocks.append({
                "symbol": t,
                "name": name,
                "motivation": "",            # kan fyllas i av användaren eller AI
                "current_price_sek": price,  # just nu i USD, kan konverteras till SEK senare
                "recommended_amount": None
            })
        except:
            stocks.append({
                "symbol": t,
                "name": t,
                "motivation": "",
                "current_price_sek": None,
                "recommended_amount": None
            })

    return jsonify({"stocks": stocks})

@app.route("/")
def home():
    return jsonify({"message": "Servern fungerar! Prova /portfolio?tickers=AAPL,TSLA"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
