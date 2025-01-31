import streamlit as st
import pandas as pd

def render_trading_decisions(result):
    st.subheader("Trading Decisions")

    if not result or not result.get("decisions"):
        st.warning("No trading decisions available yet.")
        return

    for ticker, decision in result["decisions"].items():
        st.markdown(f"#### {ticker}")

        action = decision.get("action", "").upper()
        action_color = {
            "BUY": "green",
            "SELL": "red",
            "HOLD": "orange"
        }.get(action, "gray")

        # Main decision display
        st.markdown(f"""
        <div style='padding: 10px; border-radius: 5px; background-color: {action_color}25;'>
            <b>Action:</b> :{action_color}[{action}]<br>
            <b>Quantity:</b> {decision.get('quantity', 0)}<br>
            <b>Confidence:</b> {decision.get('confidence', 0):.1f}%<br>
            <b>Reasoning:</b> {decision.get('reasoning', 'No reasoning provided')}
        </div>
        """, unsafe_allow_html=True)

        # Handle special case where action is "hold" due to error
        if (action == "HOLD" and
            decision.get('confidence', 0) == 0.0 and
            "Error" in decision.get('reasoning', '')):
            st.warning(
                icon=":material/info:",
                body="This is a fallback decision due to an error. Check error details for more information."
            )

        # Error details display
        if decision.get('error_details'):
            with st.expander("Error Details", expanded=False):
                st.error("An error occurred during decision making", icon=":material/warning:")
                st.code(decision['error_details'], language="text", wrap_lines=True)
