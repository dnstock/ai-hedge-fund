import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_analyst_signals(result):
    st.subheader("Analyst Signals")

    analyst_signals = result.get("analyst_signals", {})

    for ticker in result.get("decisions", {}).keys():
        st.write(f"**{ticker} Analysis**")

        signal_data = []
        for agent, signals in analyst_signals.items():
            if ticker in signals:
                signal = signals[ticker]
                if isinstance(signal, dict):
                    signal_data.append({
                        "Analyst": agent.replace("_agent", "").replace("_", " ").title(),
                        "Signal": signal.get("signal", "").upper(),
                        "Confidence": f"{signal.get('confidence', 0):.1f}%"
                    })

        df = pd.DataFrame(signal_data)

        # Color-code the signals
        def color_signals(val):
            if 'BULLISH' in str(val):
                return 'background-color: #90EE90'
            elif 'BEARISH' in str(val):
                return 'background-color: #FFB6C1'
            return ''

        st.dataframe(df.style.map(color_signals, subset=['Signal']))
