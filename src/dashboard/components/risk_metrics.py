import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dashboard.utils.risk_calculations import calculate_portfolio_metrics

def render_risk_metrics(result, portfolio):
    st.subheader("Risk Metrics")

    if not result or not result.get('analyst_signals'):
        st.warning("No data available for risk metrics")
        return

    # Calculate risk metrics
    risk_metrics = calculate_portfolio_metrics(result, portfolio)

    # Create metrics display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Portfolio Beta", f"{risk_metrics['portfolio_beta']:.2f}")
    with col2:
        st.metric("Sharpe Ratio", f"{risk_metrics['sharpe_ratio']:.2f}")
    with col3:
        st.metric("Value at Risk (95%)", f"${risk_metrics['var']:.2f}")

    # Create risk visualization
    fig = go.Figure()

    # Add efficient frontier if available
    if 'efficient_frontier' in risk_metrics:
        ef_returns = risk_metrics['efficient_frontier']['returns']
        ef_volatility = risk_metrics['efficient_frontier']['volatility']
        fig.add_trace(go.Scatter(
            x=ef_volatility,
            y=ef_returns,
            name='Efficient Frontier',
            line=dict(color='blue', dash='dash')
        ))

    # Add current portfolio point
    fig.add_trace(go.Scatter(
        x=[risk_metrics['portfolio_volatility']],
        y=[risk_metrics['portfolio_return']],
        mode='markers',
        name='Current Portfolio',
        marker=dict(size=10, color='red')
    ))

    fig.update_layout(
        title='Risk-Return Analysis',
        xaxis_title='Volatility',
        yaxis_title='Expected Return',
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
