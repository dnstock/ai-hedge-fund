import streamlit as st
import pandas as pd

def render_trading_decisions(result):
    st.subheader("Trading Decisions")

    if not result or not result.get("decisions"):
        st.warning("No trading decisions available yet.")
        return

    for ticker, decision in result["decisions"].items():
        # Extract decision details
        action = decision.get("action", "").upper()
        action_color_rgb = {
            "BUY": "0,128,0",         # Green
            "SELL": "255,0,0",        # Red
            "HOLD": "255,165,0"       # Orange
        }.get(action, "128,128,128")  # Gray

        # Handle special case where action is "hold" due to error
        help_text = None
        if (action == "HOLD" and
            decision.get('confidence', 0) == 0.0 and
            "Error" in decision.get('reasoning', '')):
            help_text = "This is a fallback decision due to an error. Check error details for more information."
            # st.warning(help_text, icon=":material/info:")

        # Main decision display
        st.markdown(f"""
        <div style='
            padding: 10px;
            border-radius: 5px;
            border: 2px solid rgb({action_color_rgb});
            margin-bottom: 10px;
            background-color: rgba({action_color_rgb},0.1);
        '>
            <b>{ticker}</b><br>
            <b>Action:</b> <span style='color: rgb({action_color_rgb})'>{action}</span><br>
            <b>Quantity:</b> {decision.get('quantity', 0)}<br>
            <b>Confidence:</b> {decision.get('confidence', 0):.1f}%<br>
            <b>Reasoning:</b> {decision.get('reasoning', 'No reasoning provided')}
        </div>
        """, unsafe_allow_html=True, help=help_text)

        # Error details display
        if decision.get('error_details'):
            with st.expander("Error Details", expanded=False):
                st.error("An error occurred during decision making", icon=":material/warning:")
                st.code(decision['error_details'], language="text", wrap_lines=True)
            st.divider()
