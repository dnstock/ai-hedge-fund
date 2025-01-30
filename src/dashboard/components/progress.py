import streamlit as st
from datetime import datetime
from typing import Dict, Optional

class StreamlitProgress:
    """Progress tracker that uses Streamlit for display"""

    def __init__(self):
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {}
        if 'progress_active' not in st.session_state:
            st.session_state.progress_active = False
        if 'trading_output' not in st.session_state:
            st.session_state.trading_output = None

    def start(self):
        """Start the progress tracking"""
        st.session_state.agent_status = {}
        st.session_state.progress_active = True
        st.session_state.trading_output = None

    def stop(self):
        """Stop the progress tracking"""
        st.session_state.progress_active = False

    def update_status(self, agent_name: str, ticker: Optional[str] = None, status: str = ""):
        """Update the status of an agent"""
        if not st.session_state.progress_active:
            return

        agent_display = agent_name.replace("_agent", "").replace("_", " ").title()
        key = f"{agent_display}-{ticker if ticker else 'all'}"

        st.session_state.agent_status[key] = {
            "agent": agent_display,
            "ticker": ticker,
            "status": status,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    def set_trading_output(self, output: Dict):
        """Store trading output for display"""
        st.session_state.trading_output = output

def render_progress():
    """Render the progress display in Streamlit"""
    if not st.session_state.progress_active and not st.session_state.trading_output:
        return

    # Create two columns for progress and results
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.session_state.progress_active:
            st.markdown("### Analysis Progress")

            # Create columns for the progress display
            cols = st.columns([2, 1, 2, 1])
            cols[0].write("**Agent**")
            cols[1].write("**Ticker**")
            cols[2].write("**Status**")
            cols[3].write("**Time**")

            # Sort status entries
            def sort_key(item):
                agent = item[1]["agent"]
                if "Risk Management" in agent:
                    return (2, agent)
                elif "Portfolio Management" in agent:
                    return (3, agent)
                return (1, agent)

            for key, status in sorted(st.session_state.agent_status.items(), key=sort_key):
                cols = st.columns([2, 1, 2, 1])

                # Color the status
                status_color = "green" if status["status"].lower() == "done" else \
                            "red" if "failed" in status["status"].lower() else \
                            "orange"

                cols[0].write(status["agent"])
                cols[1].write(status["ticker"] if status["ticker"] else "")
                cols[2].markdown(f":{status_color}[{status['status']}]")
                cols[3].write(status["timestamp"])

    with col2:
        if st.session_state.trading_output:
            st.markdown("### Trading Decisions")

            # Display decisions for each ticker
            for ticker, decision in st.session_state.trading_output.get("decisions", {}).items():
                st.markdown(f"#### {ticker}")

                # Create a color-coded box for the decision
                action = decision.get("action", "").upper()
                action_color = {
                    "BUY": "green",
                    "SELL": "red",
                    "HOLD": "orange"
                }.get(action, "gray")

                st.markdown(f"""
                <div style='padding: 10px; border-radius: 5px; background-color: {action_color}25;'>
                    <b>Action:</b> :{action_color}[{action}]<br>
                    <b>Quantity:</b> {decision.get('quantity', 0)}<br>
                    <b>Confidence:</b> {decision.get('confidence', 0):.1f}%
                </div>
                """, unsafe_allow_html=True)

                # Display analyst signals
                st.markdown("##### Analyst Signals")
                signals = st.session_state.trading_output.get("analyst_signals", {})
                for agent, agent_signals in signals.items():
                    if ticker in agent_signals:
                        signal = agent_signals[ticker]
                        signal_color = {
                            "BULLISH": "green",
                            "BEARISH": "red",
                            "NEUTRAL": "orange"
                        }.get(signal.get("signal", "").upper(), "gray")

                        agent_name = agent.replace("_agent", "").replace("_", " ").title()
                        st.markdown(f"- {agent_name}: :{signal_color}[{signal.get('signal', '').upper()}] ({signal.get('confidence', 0):.1f}%)")

# Create a global instance
progress = StreamlitProgress()
