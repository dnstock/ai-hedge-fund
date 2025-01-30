import streamlit as st
from datetime import datetime

class StreamlitProgress:
    """Progress tracker that uses Streamlit for display"""

    def __init__(self):
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {}
        if 'progress_active' not in st.session_state:
            st.session_state.progress_active = False

    def start(self):
        """Start the progress tracking"""
        st.session_state.agent_status = {}
        st.session_state.progress_active = True

    def stop(self):
        """Stop the progress tracking"""
        st.session_state.progress_active = False

    def update_status(self, agent_name: str, ticker: str = None, status: str = ""):
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

def render_progress():
    """Render the progress display in Streamlit"""
    if not st.session_state.progress_active:
        return

    st.markdown("### Analysis Progress")

    # Create columns for the progress display
    cols = st.columns([2, 1, 2, 1])
    cols[0].write("**Agent**")
    cols[1].write("**Ticker**")
    cols[2].write("**Status**")
    cols[3].write("**Time**")

    # Sort status entries to keep Risk Management and Portfolio Management at the bottom
    def sort_key(item):
        agent = item[1]["agent"]
        if "Risk Management" in agent:
            return (2, agent)
        elif "Portfolio Management" in agent:
            return (3, agent)
        return (1, agent)

    # Display status entries
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

# Create a global instance
progress = StreamlitProgress()
