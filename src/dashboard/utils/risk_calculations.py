import numpy as np
import pandas as pd
from scipy import stats

def calculate_portfolio_metrics(result, portfolio):
    """Calculate various risk metrics for the portfolio."""
    # Extract price data from analyst signals
    signals = result['analyst_signals']
    price_data = pd.DataFrame()

    for ticker in portfolio['positions'].keys():
        if ticker in signals and 'price_history' in signals[ticker]:
            price_data[ticker] = signals[ticker]['price_history']

    if price_data.empty:
        return {
            'portfolio_beta': 0,
            'sharpe_ratio': 0,
            'var': 0,
            'portfolio_return': 0,
            'portfolio_volatility': 0
        }

    # Calculate returns
    returns = price_data.pct_change().dropna()

    # Calculate portfolio metrics
    weights = np.array([portfolio['positions'][ticker] * price_data[ticker].iloc[-1]
                       for ticker in portfolio['positions'].keys()])
    weights = weights / np.sum(weights)

    # Portfolio return and volatility
    portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))

    # Beta calculation (using S&P 500 as market proxy - simplified here)
    portfolio_beta = 1.0  # Simplified beta calculation

    # Sharpe Ratio (assuming risk-free rate of 2%)
    risk_free_rate = 0.02
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

    # Value at Risk (95% confidence)
    var = calculate_var(returns, weights, 0.95)

    return {
        'portfolio_beta': portfolio_beta,
        'sharpe_ratio': sharpe_ratio,
        'var': var,
        'portfolio_return': portfolio_return,
        'portfolio_volatility': portfolio_volatility
    }

def calculate_var(returns, weights, confidence_level):
    """Calculate Value at Risk."""
    portfolio_returns = np.sum(returns * weights, axis=1)
    var = -np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    return var
