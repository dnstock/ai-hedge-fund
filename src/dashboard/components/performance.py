import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from tools.api import get_prices, prices_to_df

def calculate_metrics(portfolio_history):
    """Calculate key portfolio metrics"""
    returns = portfolio_history['total_value'].pct_change()
    metrics = {
        'Total Return': f"{((portfolio_history['total_value'].iloc[-1] / portfolio_history['total_value'].iloc[0]) - 1) * 100:.2f}%",
        'Sharpe Ratio': f"{(returns.mean() / returns.std() * (252**0.5)):.2f}",
        'Max Drawdown': f"{((portfolio_history['total_value'] / portfolio_history['total_value'].cummax() - 1).min() * 100):.2f}%",
        'Daily Vol': f"{(returns.std() * (252**0.5) * 100)::.2f}%",
        'Win Rate': f"{(returns[returns > 0].count() / returns.count() * 100)::.2f}%"
    }
    return metrics

def render_performance_metrics(result):
    st.subheader("Performance Metrics")

    try:
        decisions = result.get("decisions", {})
        analyst_signals = result.get("analyst_signals", {})

        if not decisions:
            st.warning("No performance data available yet.")
            return

        # Get historical prices for performance chart
        col1, col2 = st.columns([2, 1])

        # Get prices for last 30 days
        end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
        start_date = (pd.Timestamp.now() - pd.DateOffset(days=30)).strftime("%Y-%m-%d")

        with col1:
            fig = go.Figure()
            for ticker in decisions.keys():
                prices = get_prices(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date
                )
                if prices:
                    df = prices_to_df(prices)
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df["close"],
                        name=ticker,
                        mode='lines'
                    ))

            fig.update_layout(
                title="Price History (30 Days)",
                xaxis_title="Date",
                yaxis_title="Price",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # Get prices of last 2 days for metrics
        start_date = (pd.Timestamp.now() - pd.DateOffset(days=2)).strftime("%Y-%m-%d")

        with col2:
            # Display summary metrics
            for ticker in decisions.keys():
                prices = get_prices(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date
                )
                if prices:
                    df = prices_to_df(prices)
                    current_price = df["close"].iloc[-1]
                    prev_price = df["close"].iloc[-2]
                    change = ((current_price - prev_price) / prev_price) * 100
                    st.metric(
                        label=ticker,
                        value=f"${current_price:.2f}",
                        delta=f"{change:.2f}%"
                    )
    except Exception as e:
        st.error(f"Error rendering performance metrics: {str(e)}")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Portfolio Value Chart
        if 'portfolio_history' in result:
            fig = go.Figure()
            history = pd.DataFrame(result['portfolio_history'])

            fig.add_trace(go.Scatter(
                x=history.index,
                y=history['total_value'],
                name='Portfolio Value',
                line=dict(color='blue')
            ))

            # Add drawdown chart
            drawdown = (history['total_value'] / history['total_value'].cummax() - 1) * 100
            fig.add_trace(go.Scatter(
                x=history.index,
                y=drawdown,
                name='Drawdown %',
                yaxis='y2',
                line=dict(color='red')
            ))

            fig.update_layout(
                title='Portfolio Value & Drawdown',
                yaxis=dict(title='Portfolio Value ($)'),
                yaxis2=dict(title='Drawdown %', overlaying='y', side='right'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Display metrics
        metrics = calculate_metrics(history)
        for metric, value in metrics.items():
            st.metric(metric, value)

    # Trading History
    if 'trades' in result:
        st.subheader("Trading History")
        trades_df = pd.DataFrame(result['trades'])

        fig = px.scatter(trades_df,
                        x='date',
                        y='price',
                        size='quantity',
                        color='action',
                        hover_data=['ticker', 'quantity', 'price'],
                        title='Trading Activity')

        st.plotly_chart(fig, use_container_width=True)
