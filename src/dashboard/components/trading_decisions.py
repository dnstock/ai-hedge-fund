import streamlit as st
import pandas as pd

def render_trading_decisions(result):
    st.subheader("Trading Decisions")

    decisions = result.get("decisions", {})
    decision_data = []

    for ticker, decision in decisions.items():
        decision_data.append({
            "Ticker": ticker,
            "Action": decision.get("action", "").upper(),
            "Quantity": decision.get("quantity", 0),
            "Confidence": f"{decision.get('confidence', 0):.1f}%"
        })

    df = pd.DataFrame(decision_data)

    # Color-code the actions
    def color_actions(val):
        if 'BUY' in str(val):
            return 'background-color: #90EE90'
        elif 'SELL' in str(val):
            return 'background-color: #FFB6C1'
        return ''

    st.dataframe(df.style.map(color_actions, subset=['Action']))

    # Display detailed reasoning if available
    if st.checkbox("Show Decision Reasoning"):
        for ticker, decision in decisions.items():
            if "reasoning" in decision:
                st.write(f"**{ticker} Reasoning:**")
                st.write(decision["reasoning"])
