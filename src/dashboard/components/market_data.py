import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from tools.api import get_prices, prices_to_df, get_company_news

def render_market_data(tickers):
    st.subheader("Market Data")

    # Market Overview
    cols = st.columns(len(tickers))

    for i, ticker in enumerate(tickers):
        with cols[i]:
            prices = get_prices(ticker, limit=2)
            if prices:
                df = prices_to_df(prices)
                current_price = df['close'].iloc[-1]
                prev_price = df['close'].iloc[-2]
                change_pct = (current_price - prev_price) / prev_price * 100

                st.metric(
                    ticker,
                    f"${current_price:.2f}",
                    f"{change_pct:+.2f}%",
                    delta_color="normal"
                )

    # Price Chart
    selected_ticker = st.selectbox("Select Ticker for Detail View", tickers)
    timeframe = st.select_slider(
        "Select Timeframe",
        options=['1D', '5D', '1M', '3M', '6M', '1Y'],
        value='1M'
    )

    # Convert timeframe to days
    days_map = {'1D': 1, '5D': 5, '1M': 30, '3M': 90, '6M': 180, '1Y': 365}
    days = days_map[timeframe]

    prices = get_prices(selected_ticker, limit=days)
    if prices:
        df = prices_to_df(prices)

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])

        fig.update_layout(
            title=f"{selected_ticker} Price Chart",
            yaxis_title='Price',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # News Feed
        st.subheader(f"Latest News - {selected_ticker}")
        news = get_company_news(selected_ticker, limit=5)

        for article in news:
            with st.expander(f"{article.headline} - {article.date}"):
                st.write(article.summary)
                st.write(f"Sentiment: {article.sentiment}")
                if article.url:
                    st.markdown(f"[Read More]({article.url})")
