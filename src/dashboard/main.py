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
from dashboard.components.progress import render_progress, progress

def main():
    st.set_page_config(page_title="AI Hedge Fund Dashboard", layout="wide")

    st.title("AI Hedge Fund Dashboard")

    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = None

    # Sidebar settings
    with st.sidebar:
        st.title("Settings")

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
                    selected_analysts=selected_analysts
                )

                # Store results and update progress display
                st.session_state.result = result
                st.session_state.portfolio = portfolio
                st.session_state.tickers = tickers
                progress.set_trading_output(result)

    # Add progress display at the top of the dashboard
    render_progress()

    # Main dashboard layout
    if st.session_state.result is not None:
        tabs = st.tabs(["Portfolio", "Analysis", "Performance"])

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
    else:
        st.info("👈 Configure your settings and click 'Run Analysis' to start")

if __name__ == "__main__":
    main()
