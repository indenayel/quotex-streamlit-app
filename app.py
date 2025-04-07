import streamlit as st
import pandas as pd
import numpy as np
import pandas_ta as ta
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import CommandHandler, Updater
import nest_asyncio

nest_asyncio.apply()  # Fix asyncio issue for Streamlit

# Initialize Telegram bot
bot = Bot(token="YOUR_BOT_TOKEN")
chat_id = "YOUR_CHAT_ID"

# Streamlit app title
st.title("Quotex Signal Bot")

# Fetch asset data from Yahoo Finance
@st.cache
def fetch_data(symbol="EURUSD=X"):
    data = yf.download(symbol, period="7d", interval="1m")
    return data

# Function to calculate indicators
def calculate_indicators(data):
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['EMA'] = ta.ema(data['Close'], length=14)
    data['MACD'] = ta.macd(data['Close'], fast=12, slow=26, signal=9)['MACD']
    data['BB_upper'], data['BB_middle'], data['BB_lower'] = ta.bbands(data['Close'], length=20)
    return data

# Function to generate trading signals
def generate_signal(data):
    latest = data.iloc[-1]
    signal = "None"
    
    if latest['RSI'] < 30 and latest['Close'] > latest['EMA']:
        signal = "BUY"
    elif latest['RSI'] > 70 and latest['Close'] < latest['EMA']:
        signal = "SELL"
    
    return signal

# Function to send signal via Telegram
def send_telegram_message(message):
    bot.send_message(chat_id=chat_id, text=message)

# Display the most recent data
data = fetch_data()
data = calculate_indicators(data)

# Plot chart
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(data.index, data['Close'], label="Price", color='blue')
ax.set_title("Price Chart")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
st.pyplot(fig)

# Generate trading signal
signal = generate_signal(data)
st.write(f"**Signal:** {signal}")

# Send signal to Telegram
if signal != "None":
    send_telegram_message(f"New Signal: {signal} for EURUSD")

# Telegram Commands
def start(update, context):
    update.message.reply_text("Quotex Signal Bot is now running!")

def status(update, context):
    update.message.reply_text(f"Current Signal: {signal}")

# Set up the updater for the bot
updater = Updater(token="YOUR_BOT_TOKEN", use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("status", status))

# Start the bot
updater.start_polling()

# Allow the bot to run until manually stopped
updater.idle()


