import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dashboard.utils.risk_calculations import calculate_portfolio_metrics
from dashboard.utils.help_text import RISK_HELP

def render_risk_metrics(result, portfolio):
    st.subheader("Risk Metrics")

    # Add help button in the header
    with st.expander("Understanding Risk Metrics", icon=":material/modeling:"):
        st.write("""
        These metrics help you understand your portfolio's risk profile and its
        relationship with potential returns.

        Hover over the **question mark** next to each metric for detailed explanations.
        """)

    if not result or not result.get('analyst_signals'):
        st.warning("No data available for risk metrics")
        return

    # Calculate risk metrics
    risk_metrics = calculate_portfolio_metrics(result, portfolio)

    # Create metrics with help tooltips
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Portfolio Beta",
            value=f"{risk_metrics['portfolio_beta']:.2f}",
            help=RISK_HELP["portfolio_beta"]
        )
    with col2:
        st.metric(
            label="Sharpe Ratio",
            value=f"{risk_metrics['sharpe_ratio']:.2f}",
            help=RISK_HELP["sharpe_ratio"]
        )
    with col3:
        st.metric(
            label="Value at Risk (95%)",
            value=f"${risk_metrics['var']:.2f}",
            help=RISK_HELP["var"]
        )

    # Risk-Return Plot with explanation
    st.subheader("Risk-Return Analysis")
    st.caption(RISK_HELP["risk_return_plot"])

    # Add legend explanation
    with st.expander("Understanding This Graph", icon=":material/legend_toggle:"):
        st.write("""
        **Efficient Frontier** (blue dashed line) - {}

        **Current Portfolio** (🔴) - {}
        """.format(
            RISK_HELP["efficient_frontier"],
            RISK_HELP["current_portfolio"]
        ))

    # Add efficient frontier if available
    if 'efficient_frontier' in risk_metrics:
        # Create risk visualization
        fig = go.Figure()

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
    else:
        st.warning("No efficient frontier available yet.")
