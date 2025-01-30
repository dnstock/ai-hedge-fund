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

    # Create portfolio summary table with market values
    portfolio_data = []
    for ticker in tickers:
        shares = portfolio["positions"].get(ticker, 0)
        # Convert '-' to 0 and ensure numeric types
        if isinstance(shares, str) and shares == '-':
            shares = 0
        try:
            shares = float(shares)  # Convert to float first
            prices = get_prices(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
            if prices:
                current_price = prices_to_df(prices)["close"].iloc[-1]
                market_value = shares * current_price  # Also called position value
                weight = market_value / portfolio["cash"] if portfolio["cash"] > 0 else 0.0
                market_cap = None # get_market_cap(ticker, end_date)  # Skip for now to avoid API rate limits
                portfolio_data.append({
                    "Ticker": str(ticker),
                    "Shares": shares,
                    "Current Price": current_price,
                    "Market Value": market_value,
                    "Weight": weight * 100,
                    "Market Cap": market_cap if market_cap else -1,
                })
        except (ValueError, TypeError) as e:
            print(f"Error converting data for {ticker}: {e}")
            portfolio_data.append({
                "Ticker": str(ticker),
                "Shares": 0.0,
                "Current Price": 0.0,
                "Market Value": 0.0,
                "Weight": 0.0,
                "Market Cap": 0.0,
            })

    # Create DataFrame with explicit types
    df = pd.DataFrame(portfolio_data).astype({
        'Ticker': 'str',
        'Shares': 'float64',
        'Current Price': 'float64',
        'Market Value': 'float64',
        'Weight': 'float64',
        'Market Cap': 'float64',
    })

    # Add cash position
    cash_row = pd.DataFrame([{
        'Ticker': 'CASH',
        'Shares': '-',
        'Current Price': '-',
        'Market Value': float(portfolio["cash"]),
        'Weight': 100.0 - df['Weight'].sum(),
        'Market Cap': -1,
    }])

    # Combine portfolio positions with cash
    df = pd.concat([df, cash_row], ignore_index=True)

    # Format the display
    formatted_df = df.copy()
    formatted_df['Market Value'] = formatted_df['Market Value'].map('${:,.2f}'.format)
    formatted_df['Weight'] = formatted_df['Weight'].map('{:.1f}%'.format)
    # Only format numeric values
    formatted_df['Current Price'] = formatted_df['Current Price'].apply(
        lambda x: '${:,.2f}'.format(x) if isinstance(x, (int, float)) else x
    )
    formatted_df['Shares'] = formatted_df['Shares'].apply(
        lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x
    )
    # Only format if available
    formatted_df['Market Cap'] = formatted_df['Market Cap'].apply(
        lambda x: '${:,.0f}'.format(x) if x >= 0 else '-'
    )

    # Display the portfolio
    st.dataframe(
        formatted_df,
        column_config={
            "Ticker": "Asset",
            "Shares": "Shares",
            "Current Price": "Price",
            "Market Value": "Market Value",
            "Weight": "Weight (%)",
            "Market Cap": "Market Cap",
        },
        hide_index=True
    )

    # Display total portfolio value
    total_value = df['Market Value'].sum()
    st.metric(
        label="Total Portfolio Value",
        value=f"${total_value:,.2f}"
    )

    # Portfolio composition pie chart
    fig = go.Figure(data=[go.Pie(
        labels=[d["Ticker"] for d in portfolio_data],
        values=[float(d["Market Value"]) for d in portfolio_data],
        hole=.3
    )])
    fig.update_layout(title="Portfolio Composition")
    st.plotly_chart(fig)
