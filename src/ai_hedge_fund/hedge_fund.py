from typing import List, Dict, Optional
from datetime import datetime
from .types import TradingDecision, PortfolioState, BacktestResult, AnalystSignal
from ..main import run_hedge_fund
from ..backtester import Backtester

class AIHedgeFund:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        margin_requirement: float = 0.0,
        model_name: str = "gpt-4",
        model_provider: str = "OpenAI",
        selected_analysts: Optional[List[str]] = None
    ):
        self.initial_capital = initial_capital
        self.margin_requirement = margin_requirement
        self.model_name = model_name
        self.model_provider = model_provider
        self.selected_analysts = selected_analysts or []

    def trade(
        self,
        tickers: List[str],
        portfolio: Optional[PortfolioState] = None,
    ) -> Dict[str, TradingDecision]:
        """
        Make trading decisions for the given tickers based on current market conditions.
        
        Args:
            tickers: List of stock symbols to analyze
            portfolio: Current portfolio state (optional)
            
        Returns:
            Dictionary mapping tickers to trading decisions
        """
        if portfolio is None:
            portfolio = self._initialize_portfolio(tickers)

        end_date = datetime.now().strftime("%Y-%m-%d")

        result = run_hedge_fund(
            tickers=tickers,
            start_date=None,  # Will use default lookback
            end_date=end_date,
            portfolio=portfolio,
            model_name=self.model_name,
            model_provider=self.model_provider,
            selected_analysts=self.selected_analysts
        )

        return result["decisions"]

    def backtest(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
    ) -> BacktestResult:
        """
        Run a backtest simulation.
        
        Args:
            tickers: List of stock symbols to trade
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            BacktestResult containing performance metrics and portfolio values
        """
        backtester = Backtester(
            agent=run_hedge_fund,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            model_name=self.model_name,
            model_provider=self.model_provider,
            selected_analysts=self.selected_analysts,
            initial_margin_requirement=self.margin_requirement,
        )

        metrics = backtester.run_backtest()
        performance_df = backtester.analyze_performance()

        return BacktestResult(
            portfolio_values=backtester.portfolio_values,
            total_return=metrics.get("total_return", 0.0),
            sharpe_ratio=metrics.get("sharpe_ratio", 0.0),
            max_drawdown=metrics.get("max_drawdown", 0.0),
            win_rate=metrics.get("win_rate", 0.0),
            analyst_signals=backtester.last_analyst_signals
        )

    def _initialize_portfolio(self, tickers: List[str]) -> PortfolioState:
        """Create an initial portfolio state."""
        return {
            "cash": self.initial_capital,
            "margin_used": 0.0,
            "positions": {
                ticker: {
                    "long": 0,
                    "short": 0,
                    "long_cost_basis": 0.0,
                    "short_cost_basis": 0.0,
                    "short_margin_used": 0.0
                } for ticker in tickers
            },
            "realized_gains": {
                ticker: {
                    "long": 0.0,
                    "short": 0.0
                } for ticker in tickers
            }
        }
