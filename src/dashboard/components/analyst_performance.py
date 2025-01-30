import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def calculate_analyst_accuracy(signals_history):
    """Calculate accuracy metrics for each analyst"""
    accuracies = {}
    for analyst, signals in signals_history.items():
        correct_calls = 0
        total_calls = 0

        for signal in signals:
            if signal['actual_return'] > 0 and signal['signal'] == 'bullish':
                correct_calls += 1
            elif signal['actual_return'] < 0 and signal['signal'] == 'bearish':
                correct_calls += 1
            total_calls += 1

        if total_calls > 0:
            accuracies[analyst] = {
                'accuracy': correct_calls / total_calls * 100,
                'total_calls': total_calls,
                'correct_calls': correct_calls
            }

    return accuracies

def render_analyst_performance(result):
    st.subheader("Analyst Performance")

    if 'analyst_signals_history' in result:
        # Calculate performance metrics
        accuracies = calculate_analyst_accuracy(result['analyst_signals_history'])

        # Create accuracy chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(accuracies.keys()),
                y=[acc['accuracy'] for acc in accuracies.values()],
                text=[f"{acc['accuracy']:.1f}%" for acc in accuracies.values()],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title='Analyst Signal Accuracy',
            yaxis_title='Accuracy %',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show detailed metrics
        col1, col2, col3 = st.columns(3)

        for analyst, metrics in accuracies.items():
            with col1:
                st.metric(f"{analyst} Accuracy", f"{metrics['accuracy']:.1f}%")
            with col2:
                st.metric(f"{analyst} Total Signals", metrics['total_calls'])
            with col3:
                st.metric(f"{analyst} Correct Signals", metrics['correct_calls'])
