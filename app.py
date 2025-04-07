
import streamlit as st
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta

st.set_page_config(page_title="Quotex AI Signals", layout="centered")

# Header
st.title("📈 Quotex AI Signal Dashboard")
st.markdown("Real-time market-based signals using technical indicators.")

# Assets to monitor
assets = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "NASDAQ": "^IXIC",
    "Gold": "GC=F",
    "Oil": "CL=F",
    "Apple": "AAPL",
    "Ethereum": "ETH-USD"
}

# Parameters
interval = "1m"
lookback_minutes = 120

def get_signals(ticker):
    try:
        df = yf.download(ticker, period="2h", interval=interval)
        df.dropna(inplace=True)
        df["EMA"] = ta.ema(df["Close"], length=9)
        df["RSI"] = ta.rsi(df["Close"], length=14)
        macd = ta.macd(df["Close"])
        df["MACD"] = macd["MACD_12_26_9"]
        df["Signal"] = macd["MACDs_12_26_9"]
        bb = ta.bbands(df["Close"])
        df["BB_upper"] = bb["BBU_20_2.0"]
        df["BB_lower"] = bb["BBL_20_2.0"]

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signal = "Neutral"

        # Signal logic
        if latest["RSI"] < 30 and latest["Close"] < latest["BB_lower"]:
            signal = "🔼 Buy (Oversold)"
        elif latest["RSI"] > 70 and latest["Close"] > latest["BB_upper"]:
            signal = "🔽 Sell (Overbought)"
        elif latest["EMA"] > latest["Close"] and latest["MACD"] < latest["Signal"]:
            signal = "🔽 Sell"
        elif latest["EMA"] < latest["Close"] and latest["MACD"] > latest["Signal"]:
            signal = "🔼 Buy"

        return {
            "price": round(latest["Close"], 4),
            "signal": signal,
            "rsi": round(latest["RSI"], 2),
            "macd": round(latest["MACD"], 2),
            "ema": round(latest["EMA"], 2)
        }
    except Exception as e:
        return {"error": str(e)}

# Show signals
for name, ticker in assets.items():
    st.subheader(f"{name}")
    with st.spinner("Analyzing..."):
        data = get_signals(ticker)
        if "error" in data:
            st.error(data["error"])
        else:
            st.markdown(f"**Price:** {data['price']}")
            st.markdown(f"**Signal:** {data['signal']}")
            st.markdown(f"**RSI:** {data['rsi']} | **MACD:** {data['macd']} | **EMA:** {data['ema']}")
    st.divider()
