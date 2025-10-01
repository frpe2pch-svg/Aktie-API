from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route("/portfolio")
def portfolio():
    # Hämta tickers från Lovable (query-param)
    tickers_param = request.args.get("tickers", "")
    tickers = [t.strip().upper() for t in tickers_param.split(",") if t.strip()]

    if not tickers:
        return jsonify({"error": "Ingen ticker angiven. Lovable måste skicka tickers."})

    stocks = []

    for t in tickers:
        try:
            df = yf.download(t, period="1mo", interval="1wk", progress=False, threads=False, auto_adjust=False)
            price = round(float(df["Close"].iloc[-1]), 2) if not df.empty else None

            info = yf.Ticker(t).info
            name = info.get("shortName") or t

            stocks.append({
                "symbol": t,
                "name": name,
                "motivation": "",            # Tom motivation, kan fyllas av Lovable/AI
                "current_price_sek": price,  # Just nu USD
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
