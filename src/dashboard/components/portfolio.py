from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from tools.api import get_prices, get_market_cap, prices_to_df

def render_portfolio_view(portfolio, tickers):
    st.subheader("Portfolio Overview")

    # Get today's date for price lookup
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Create portfolio summary table
    portfolio_data = []
    total_value = portfolio["cash"]

    for ticker in tickers:
        prices = get_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        if prices:
            current_price = prices_to_df(prices)["close"].iloc[-1]
            position_value = portfolio["positions"][ticker] * current_price
            total_value += position_value
            market_cap = get_market_cap(ticker, end_date)

            portfolio_data.append({
                "Ticker": ticker,
                "Shares": portfolio["positions"][ticker],
                "Current Price": f"${current_price:.2f}",
                "Position Value": f"${position_value:.2f}",
                "Weight": f"{(position_value/total_value*100):.1f}%",
                "Market Cap": f"${market_cap:,.0f}" if market_cap else "N/A",
            })

    # Add cash position
    portfolio_data.append({
        "Ticker": "Cash",
        "Shares": "-",
        "Current Price": "-",
        "Position Value": f"${portfolio['cash']:.2f}",
        "Weight": f"{(portfolio['cash']/total_value*100):.1f}%"
    })

    st.dataframe(pd.DataFrame(portfolio_data))

    # Portfolio composition pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[d["Ticker"] for d in portfolio_data],
        values=[float(d["Position Value"].replace("$", "").replace(",", "")) for d in portfolio_data],
        hole=.3
    )])
    fig.update_layout(title="Portfolio Composition")
    st.plotly_chart(fig)
