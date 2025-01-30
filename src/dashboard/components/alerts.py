import streamlit as st
from datetime import datetime

def render_alerts_config():
    st.sidebar.subheader("Alert Settings")

    # Price Alerts
    if st.sidebar.checkbox("Enable Price Alerts"):
        for ticker in st.session_state.get('tickers', []):
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.number_input(f"{ticker} Upper", key=f"alert_upper_{ticker}")
            with col2:
                st.number_input(f"{ticker} Lower", key=f"alert_lower_{ticker}")

    # Portfolio Alerts
    if st.sidebar.checkbox("Enable Portfolio Alerts"):
        st.sidebar.number_input(
            "Drawdown Alert (%)",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            key="alert_drawdown"
        )

        st.sidebar.number_input(
            "Daily Loss Alert (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            key="alert_daily_loss"
        )

    # Signal Alerts
    if st.sidebar.checkbox("Enable Signal Alerts"):
        st.sidebar.multiselect(
            "Alert on Signals",
            ["Strong Buy", "Strong Sell", "Analyst Disagreement"],
            default=["Strong Buy", "Strong Sell"],
            key="alert_signals"
        )

def check_alerts(result):
    alerts = []

    # Check price alerts
    for ticker in st.session_state.get('tickers', []):
        current_price = result.get('current_prices', {}).get(ticker)
        if current_price:
            upper_alert = st.session_state.get(f"alert_upper_{ticker}")
            lower_alert = st.session_state.get(f"alert_lower_{ticker}")

            if upper_alert and current_price > upper_alert:
                alerts.append(f"⚠️ {ticker} above {upper_alert}")
            if lower_alert and current_price < lower_alert:
                alerts.append(f"⚠️ {ticker} below {lower_alert}")

    # Check portfolio alerts
    if 'portfolio_history' in result:
        drawdown = st.session_state.get("alert_drawdown")
        if drawdown:
            current_drawdown = result['current_drawdown']
            if abs(current_drawdown) > drawdown:
                alerts.append(f"📉 Portfolio drawdown: {current_drawdown:.1f}%")

    return alerts
