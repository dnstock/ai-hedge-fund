from typing import Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass
class APIConfig:
    """API configuration with validation"""
    alpha_vantage_key: str
    finnhub_key: str
    alpaca_key_id: str
    alpaca_secret_key: str
    alpaca_base_url: str
    polygon_key: str
    polygon_base_url: str
    openai_key: str
    financial_datasets_key: str
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None

class Config:
    """Global configuration singleton"""
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self._load_config()
            self._is_initialized = True

    def _load_config(self):
        """Load and validate environment variables"""
        # Try to load from .env file
        load_dotenv()

        required_vars = {
            'ALPHA_VANTAGE_KEY': 'API key for Alpha Vantage',
            'FINNHUB_API_KEY': 'API key for Finnhub',
            'ALPACA_API_KEY_ID': 'API key ID for Alpaca',
            'ALPACA_API_SECRET_KEY': 'Secret key for Alpaca',
            'ALPACA_BASE_URL': 'Base URL for Alpaca API',
            'POLYGON_API_KEY': 'API key for Polygon',
            'POLYGON_BASE_URL': 'Base URL for Polygon API',
            'OPENAI_API_KEY': 'API key for OpenAI',
            'FINANCIAL_DATASETS_API_KEY': 'API key for Financial Datasets',
        }

        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{var} ({description})")

        if missing_vars:
            raise EnvironmentError(
                "Missing required environment variables:\n" +
                "\n".join(f"- {var}" for var in missing_vars)
            )

        self.api = APIConfig(
            alpha_vantage_key=os.getenv('ALPHA_VANTAGE_KEY'),
            finnhub_key=os.getenv('FINNHUB_API_KEY'),
            alpaca_key_id=os.getenv('ALPACA_API_KEY_ID'),
            alpaca_secret_key=os.getenv('ALPACA_API_SECRET_KEY'),
            alpaca_base_url=os.getenv('ALPACA_BASE_URL'),
            polygon_key=os.getenv('POLYGON_API_KEY'),
            polygon_base_url=os.getenv('POLYGON_BASE_URL'),
            openai_key=os.getenv('OPENAI_API_KEY'),
            financial_datasets_key=os.getenv('FINANCIAL_DATASETS_API_KEY'),
            langsmith_api_key=os.getenv('LANGSMITH_API_KEY'),
            langsmith_project=os.getenv('LANGSMITH_PROJECT')
        )

    @property
    def env_file_template(self) -> str:
        """Return a template for the .env file"""
        return """# API Keys Configuration
ALPHA_VANTAGE_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
ALPACA_API_KEY_ID=your_key_here
ALPACA_API_SECRET_KEY=your_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
POLYGON_API_KEY=your_key_here
POLYGON_BASE_URL=https://api.polygon.io/v2
OPENAI_API_KEY=your_key_here
FINANCIAL_DATASETS_API_KEY=your_key_here

# Optional LangSmith Configuration
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=your_project_here
"""

# Global config instance
config = Config()
