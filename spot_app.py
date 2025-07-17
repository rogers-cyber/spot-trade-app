import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# --- Page config ---
st.set_page_config(page_title="Spot Trade Simulator", layout="centered")
st.title("📈 Spot Trade Simulator")

# --- Sidebar Inputs ---
symbol = st.sidebar.text_input("🔹 Coin symbol (e.g. BTCUSDT, PEPEUSDT)", value="PEPEUSDT").upper()
investment = st.sidebar.number_input("💰 Investment (USDT)", value=20.0, min_value=1.0)
profit_pct = st.sidebar.number_input("🎯 Profit target (%)", value=2.0, min_value=0.1)
show_plot = st.sidebar.checkbox("📊 Show Price Chart", value=True)

st.markdown(f"### Simulation for `{symbol}`")
st.write(f"🔹 **Investment:** ${investment:.2f}")
st.write(f"🔹 **Target Return:** {profit_pct:.2f}%")

# --- Load Data Function ---
@st.cache_data(ttl=300)
def load_price_data(symbol, limit=200):
    base_urls = [
        "https://data.binance.com",
        "https://api.binance.us"
    ]
    for base in base_urls:
        try:
            url = f"{base}/api/v3/klines"
            params = {'symbol': symbol, 'interval': '1h', 'limit': limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=[
                    'Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                    'CloseTime', 'QAV', 'NumTrades', 'TBBase', 'TBQuote', 'Ignore'
                ])
                df['Time'] = pd.to_datetime(df['Time'], unit='ms')
                df['Close'] = df['Close'].astype(float)
                return df[['Time', 'Close']]
        except Exception:
            continue
    return pd.DataFrame()

# --- Load and Analyze ---
df = load_price_data(symbol)

if df.empty or len(df) < 20:
    st.error("❌ Unable to fetch sufficient data. Please check the coin symbol (e.g. BTCUSDT).")
    st.stop()

current_price = df['Close'].iloc[-1]
df['MA5'] = df['Close'].rolling(5).mean()
df['MA20'] = df['Close'].rolling(20).mean()
trend = "UP" if df['MA5'].iloc[-2] > df['MA20'].iloc[-2] else "DOWN"

# --- Simulation ---
token_amount = investment / current_price
target_price = current_price * (1 + profit_pct / 100)
profit_est = token_amount * (target_price - current_price)

# --- Trade Strategy ---
hold_pct, sell_pct = (80, 20) if trend == "UP" else (30, 70)
hold_amt = investment * hold_pct / 100
sell_amt = investment * sell_pct / 100

# --- Output Summary ---
st.subheader("📊 Simulation Results")
st.markdown(f"**Current Price:** `${current_price:.8f}`")
st.markdown(f"**Trend Direction:** `{trend}`")
st.markdown(f"**Target Price (+{profit_pct:.2f}%):** `${target_price:.8f}`")
st.markdown(f"**Estimated Profit:** `${profit_est:.2f}`")
st.markdown(f"**Suggested Action:** HOLD **{hold_pct}%** (${hold_amt:.2f}), SELL **{sell_pct}%** (${sell_amt:.2f})")

# --- Chart ---
if show_plot:
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(df['Time'], df['Close'], label='Price', linewidth=2)
    ax.plot(df['Time'], df['MA5'], '--', label='MA5', alpha=0.7)
    ax.plot(df['Time'], df['MA20'], '--', label='MA20', alpha=0.7)
    ax.set_title(f"{symbol} Price Trend")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# --- Donation Section ---
st.markdown("---")
st.markdown("## ☕ Donate with Crypto")
st.markdown("""
If this app helped you, consider donating:

- **BTC**: `bc1qlaact2ldakvwqa7l9xd3lhp4ggrvezs0npklte`
- **TRX / USDT (TRC20)**: `TBMrjoyxAuKTxBxPtaWB6uc9U5PX4JMfFu`
""")

try:
    st.image("eth_qr.png", width=180, caption="ETH / USDT QR")
except:
    st.info("Upload `eth_qr.png` to show a QR code for donations.")
