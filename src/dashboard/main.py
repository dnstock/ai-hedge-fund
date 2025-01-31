import os
import sys
from dotenv import load_dotenv
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

# Load environment variables
load_dotenv()

# Add PYTHONPATH from .env to sys.path
python_path = os.getenv("PYTHONPATH")
if (python_path and python_path not in sys.path):
    sys.path.insert(0, python_path)

from dashboard.components.portfolio import render_portfolio_view
from dashboard.components.analyst_signals import render_analyst_signals
from dashboard.components.trading_decisions import render_trading_decisions
from dashboard.components.performance import render_performance_metrics
from dashboard.utils.workflow import run_hedge_fund
from utils.analysts import ANALYST_ORDER
from utils.progress import progress, render_progress_display  # Update import
from dashboard.components.risk_metrics import render_risk_metrics
from dashboard.components.api_settings import render_api_settings
from llm.models import LLM_ORDER, get_model_info

def render_dashboard_progress():
    """Render progress tracking in the dashboard"""
    if "progress_container" not in st.session_state:
        st.session_state.progress_container = st.empty()

    # Process any new messages
    messages = progress.get_messages()
    state = progress.get_current_state()

    if state["running"] or state["trading_output"]:
        with st.session_state.progress_container.container():
            col1, col2 = st.columns([1, 1])

            with col1:
                if state["running"]:
                    st.markdown("### Analysis Progress")

                    # Create status table data
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
                    # ... rest of existing trading output display code ...

def main():
    st.set_page_config(page_title="AI Hedge Fund Dashboard", layout="wide")

    st.title("AI Hedge Fund Dashboard")

    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None

    # Initialize API keys from environment if not in session state
    if 'OPENAI_API_KEY' not in st.session_state:
        st.session_state.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    if 'FINANCIAL_DATASETS_API_KEY' not in st.session_state:
        st.session_state.FINANCIAL_DATASETS_API_KEY = os.getenv('FINANCIAL_DATASETS_API_KEY', '')

    # Sidebar settings
    with st.sidebar:
        # Add API settings at the top of sidebar
        render_api_settings()

        st.title("Settings")

        # Add model selection at the top
        st.subheader("Model Settings")
        model_options = [(display, value) for display, value, _ in LLM_ORDER]
        selected_model = st.selectbox(
            "Select LLM Model",
            options=[value for _, value in model_options],
            format_func=lambda x: next(display for display, value in model_options if value == x),
            help="Choose the language model to use for analysis"
        )

        # Get model info and provider
        model_info = get_model_info(selected_model)
        model_provider = model_info.provider.value if model_info else "openai"

        st.subheader("Trading Settings")

        # Ticker selection
        ticker_input = st.text_input("Enter Tickers (comma-separated)", "AAPL,MSFT,GOOGL")
        tickers = [t.strip() for t in ticker_input.split(",")]

        # Date selection
        end_date = st.date_input("End Date", datetime.now())
        lookback_period = st.selectbox(
            "Lookback Period",
            ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"],
            index=2
        )

        # Analyst selection
        st.subheader("Select Analysts")
        selected_analysts = []
        for display, value in ANALYST_ORDER:
            if st.checkbox(display, True):
                selected_analysts.append(value)

        # Initialize portfolio
        initial_cash = st.number_input("Initial Cash", value=100000.0, step=10000.0)

        # Run analysis button
        if st.sidebar.button("Run Analysis"):
            # Calculate start date based on lookback period
            period_map = {
                "1 Week": timedelta(days=7),
                "1 Month": relativedelta(months=1),
                "3 Months": relativedelta(months=3),
                "6 Months": relativedelta(months=6),
                "1 Year": relativedelta(years=1)
            }
            start_date = end_date - period_map[lookback_period]

            # Initialize portfolio
            portfolio = {
                "cash": initial_cash,
                "positions": {ticker: 0 for ticker in tickers}
            }

            with st.spinner("Running analysis..."):
                result = run_hedge_fund(
                    tickers=tickers,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    portfolio=portfolio,
                    selected_analysts=selected_analysts,
                    model_name=selected_model,
                    model_provider=model_provider
                )

                # Store results and update progress display
                st.session_state.result = result
                st.session_state.portfolio = portfolio
                st.session_state.tickers = tickers
                progress.set_trading_output(result)

    # Add progress display at the top of the dashboard
    state = progress.get_current_state()
    render_progress_display(state)

    render_dashboard_progress()

    # Main dashboard layout
    if st.session_state.result is not None:
        tabs = st.tabs(["Portfolio", "Analysis", "Performance", "Risk"])

        with tabs[0]:
            render_portfolio_view(st.session_state.portfolio, st.session_state.tickers)

        with tabs[1]:
            col1, col2 = st.columns(2)
            with col1:
                render_analyst_signals(st.session_state.result)
            with col2:
                render_trading_decisions(st.session_state.result)

        with tabs[2]:
            render_performance_metrics(st.session_state.result)

        with tabs[3]:
            render_risk_metrics(st.session_state.result, st.session_state.portfolio)
    else:
        st.info("Configure your settings and click 'Run Analysis' to start", icon=":material/west:")  # 👈

if __name__ == "__main__":
    main()
