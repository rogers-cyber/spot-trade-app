import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Streamlit Config ---
st.set_page_config(page_title="Spot Trade Simulator", layout="centered")
st.title("📈 Spot Trade Simulator")

# --- Sidebar Inputs ---
symbol = st.sidebar.text_input("🔹 Coin symbol (e.g. BTCUSDT, PEPEUSDT)", value="PEPEUSDT").upper()
investment = st.sidebar.number_input("💰 Investment (USDT)", value=20.0, min_value=1.0)
profit_pct = st.sidebar.number_input("🎯 Profit target (%)", value=2.0, min_value=0.1)
show_plot = st.sidebar.checkbox("📊 Show Price Chart", value=True)

# --- Display Basic Info ---
st.markdown(f"### Simulation for `{symbol}`")
st.write(f"🔹 **Investment:** ${investment:.2f}")
st.write(f"🔹 **Target Return:** {profit_pct:.2f}%")

# --- Load Binance Price Data ---
@st.cache_data(ttl=300)
def load_price_data(symbol, limit=200):
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': '1h', 'limit': limit}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        df = pd.DataFrame(data, columns=[
            'Time','Open','High','Low','Close','Volume',
            'CloseTime','QAV','NumTrades','TBBase','TBQuote','Ignore'
        ])
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df['Close'] = df['Close'].astype(float)
        return df[['Time', 'Close']]
    except Exception as e:
        return pd.DataFrame()

# --- Load Data ---
df = load_price_data(symbol)

if df.empty or len(df) < 20:
    st.error("❌ Unable to fetch sufficient data. Please check the coin symbol (e.g. BTCUSDT).")
    st.stop()

# --- Analysis ---
current_price = df['Close'].iloc[-1]
df['MA5'] = df['Close'].rolling(5).mean()
df['MA20'] = df['Close'].rolling(20).mean()
trend = "UP" if df['MA5'].iloc[-2] > df['MA20'].iloc[-2] else "DOWN"

# --- Simulation ---
token_amount = investment / current_price
target_price = current_price * (1 + profit_pct / 100)
profit_est = token_amount * (target_price - current_price)

# --- Strategy Decision ---
hold_pct, sell_pct = (80, 20) if trend == "UP" else (30, 70)
hold_amt = investment * hold_pct / 100
sell_amt = investment * sell_pct / 100

# --- Results ---
st.subheader("📊 Simulation Results")
st.markdown(f"**💲 Current Price:** `${current_price:.8f}`")
st.markdown(f"**📈 Trend Direction:** `{trend}`")
st.markdown(f"**🎯 Target Price (+{profit_pct:.2f}%):** `${target_price:.8f}`")
st.markdown(f"**💰 Estimated Profit:** `${profit_est:.2f}`")

# ✅ Clean Suggested Action Output
st.write("🧾 **Suggested Action**")
st.write(f"• HOLD: {hold_pct}% (${hold_amt:.2f})")
st.write(f"• SELL: {sell_pct}% (${sell_amt:.2f})")

# --- Chart ---
if show_plot:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Time'], df['Close'], label='Price', linewidth=2)
    ax.plot(df['Time'], df['MA5'], '--', label='MA5', alpha=0.7)
    ax.plot(df['Time'], df['MA20'], '--', label='MA20', alpha=0.7)
    ax.set_title(f"{symbol} Price Trend")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USDT)")
    ax.legend()
    ax.grid(True)

    # Format X-axis time labels
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

# --- Optional: Download Trade Suggestion ---
csv_data = pd.DataFrame([{
    "Symbol": symbol,
    "Current Price": current_price,
    "Trend": trend,
    "Target Price": target_price,
    "Estimated Profit": profit_est,
    "HOLD %": hold_pct,
    "HOLD Amount": hold_amt,
    "SELL %": sell_pct,
    "SELL Amount": sell_amt
}])
st.download_button(
    label="📥 Download Suggestion as CSV",
    data=csv_data.to_csv(index=False),
    file_name=f"{symbol}_trade_suggestion.csv",
    mime="text/csv"
)

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
