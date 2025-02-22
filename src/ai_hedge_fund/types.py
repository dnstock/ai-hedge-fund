from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict
from datetime import datetime

class TradingDecision(TypedDict):
    action: str  # 'buy', 'sell', 'short', 'cover', 'hold'
    quantity: float
    reasoning: Optional[str]

class PositionInfo(TypedDict):
    long: int
    short: int
    long_cost_basis: float
    short_cost_basis: float
    short_margin_used: float

class RealizedGains(TypedDict):
    long: float
    short: float

class PortfolioState(TypedDict):
    cash: float
    margin_used: float
    positions: Dict[str, PositionInfo]
    realized_gains: Dict[str, RealizedGains]

class AnalystSignal(TypedDict):
    signal: str  # 'bullish', 'bearish', 'neutral'
    confidence: float
    reasoning: str

@dataclass
class BacktestResult:
    portfolio_values: List[Dict[str, float]]
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    analyst_signals: Dict[str, Dict[str, AnalystSignal]]
