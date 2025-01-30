import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from tools.api import get_prices, prices_to_df

def render_portfolio_view(portfolio, tickers):
    st.subheader("Portfolio Overview")

    # Create portfolio summary table
    portfolio_data = []
    total_value = portfolio["cash"]

    for ticker in tickers:
        prices = get_prices(ticker=ticker, limit=1)
        if prices:
            current_price = prices_to_df(prices)["close"].iloc[-1]
            position_value = portfolio["positions"][ticker] * current_price
            total_value += position_value

            portfolio_data.append({
                "Ticker": ticker,
                "Shares": portfolio["positions"][ticker],
                "Current Price": f"${current_price:.2f}",
                "Position Value": f"${position_value:.2f}",
                "Weight": f"{(position_value/total_value*100):.1f}%"
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
