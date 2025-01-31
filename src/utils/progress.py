import streamlit as st
from datetime import datetime
from typing import Dict, Optional, List
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.style import Style
from rich.text import Text
from queue import Queue
from threading import Lock
from collections import defaultdict

console = Console()

def render_progress_display(state: Dict):
    """Render progress tracking in the Streamlit dashboard"""
    if "progress_container" not in st.session_state:
        st.session_state.progress_container = st.empty()

    if state["running"] or state["trading_output"]:
        with st.session_state.progress_container.container():
            col1, col2 = st.columns([1, 1])

            with col1:
                if state["running"]:
                    st.markdown("### Analysis Progress")
                    status_data = []
                    for agent, update in state["updates"].items():
                        status_data.append({
                            "Agent": agent.replace("_agent", "").replace("_", " ").title(),
                            "Ticker": update.get("ticker", ""),
                            "Status": update.get("status", ""),
                            "Time": update.get("timestamp", "")
                        })
                    if status_data:
                        st.table(pd.DataFrame(status_data))

            with col2:
                if state["trading_output"]:
                    st.markdown("### Trading Decisions")
                    for ticker, decision in state["trading_output"].get("decisions", {}).items():
                        st.markdown(f"#### {ticker}")
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

class ProgressTracker:
    """Unified progress tracker that works with both console and Streamlit"""

    def __init__(self):
        self.lock = Lock()
        self.message_queue = Queue()
        self.updates: Dict[str, Dict] = defaultdict(dict)
        self.running = False
        self.trading_output = None

    def start(self):
        """Start progress tracking"""
        with self.lock:
            self.running = True
            self.updates.clear()
            self.trading_output = None
            self._queue_message("system", "start", None, None)

    def stop(self):
        """Stop progress tracking"""
        with self.lock:
            self.running = False
            self._queue_message("system", "stop", None, None)

    def update_status(self, agent: str, ticker: Optional[str] = None, status: str = ""):
        """Queue a status update"""
        with self.lock:
            if self.running:
                self._queue_message(agent, "update", ticker, status)
                self.updates[agent] = {
                    "ticker": ticker,
                    "status": status,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }

    def set_trading_output(self, output):
        """Store trading output"""
        with self.lock:
            self.trading_output = output
            self._queue_message("system", "output", None, output)

    def get_messages(self) -> List[Dict]:
        """Get all queued messages (non-blocking)"""
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get_nowait())
        return messages

    def get_current_state(self) -> Dict:
        """Get current state of all updates"""
        with self.lock:
            return {
                "running": self.running,
                "updates": dict(self.updates),
                "trading_output": self.trading_output
            }

    def _queue_message(self, agent: str, msg_type: str, ticker: Optional[str], data: any):
        """Queue a message for processing"""
        self.message_queue.put({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "type": msg_type,
            "ticker": ticker,
            "data": data
        })

# Global instance
progress = ProgressTracker()
