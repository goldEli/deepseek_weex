# Project Context

## Purpose
A cryptocurrency trading bot repository implementing automated trading strategies using AI analysis. The bot primarily trades BTC/USDT futures contracts on WEEX and OKX exchanges, with market analysis powered by DeepSeek AI.

## Tech Stack
- **Language**: Python 3
- **Exchange Integration**: ccxt library
- **AI Analysis**: DeepSeek AI (via OpenAI SDK)
- **Data Analysis**: pandas
- **HTTP Requests**: requests, urllib3
- **Scheduling**: schedule
- **Environment**: python-dotenv
- **Package Manager**: uv (recommended)

## Project Conventions

### Code Style
- **File Naming**: snake_case for Python files (e.g., `deepseek_weex1.py`, `fetch_order_history.py`)
- **Strategy Files**: Prefix with `deepseek_` for main trading strategies
- **Utility Scripts**: Descriptive names indicating purpose (e.g., `close_btc_long.py`, `get_account_assets.py`)
- **Configuration**: TRADE_CONFIG dictionaries in strategy files
- **Documentation**: Minimal comments, clean code preferred

### Architecture Patterns
- **Central SDK**: `weex_sdk.py` (56KB) provides all exchange integration
  - WeexClient class for WEEX exchange operations
  - HMAC-SHA256 signature generation with BASE64 encoding
  - HTTP request handler with authentication headers
- **Strategy Pattern**: Separate strategy files for different trading approaches
- **Utility Scripts**: Single-purpose Python scripts for account/position/order management
- **Unidirectional Positions**: Only long positions (no hedging)
- **Script Execution Framework**: `run_script_selector.py` parses SCRIPT.md for commands

### Testing Strategy
- **Test Files**: Root directory test files (e.g., `test_weex.py`, `test_market_order.py`)
- **Component Testing**: Individual test files for each major component
- **Direct Execution**: Run test files directly with python3
- **No Framework**: No specific testing framework (simple assert statements)

### Git Workflow
- **Branching**: Standard git flow with main branch
- **Commit Style**: Feature-based commits with descriptive messages
- **Recent Changes**: Script selector, profit display, history orders API, API signature fixes

## Domain Context
- **Trading Focus**: BTC/USDT futures on WEEX and OKX exchanges
- **Market Analysis**: AI-powered sentiment and technical indicator analysis
- **Leverage Trading**: 10x leverage configuration
- **Risk Management**: Stop-loss and take-profit parameters
- **15-Minute Timeframes**: Standard K-line analysis period
- **Unidirectional**: Long positions only, no hedging strategy

## Important Constraints
- **Unidirectional Positions**: Cannot open short positions or hedge
- **API Keys Required**: DEEPSEEK_API_KEY, WEEX_API_KEY, WEEX_SECRET, WEEX_ACCESS_PASSPHRASE, OKX credentials
- **Test Mode Available**: All strategies support simulation mode
- **Exchange-Specific**: Different trading pairs format (WEEX: 'cmt_btcusdt', OKX: 'BTC/USDT:USDT')
- **Environment Variables**: All configuration via .env file (not committed)

## External Dependencies
- **WEEX Exchange**: Primary trading platform with futures contracts
- **OKX Exchange**: Secondary trading platform
- **DeepSeek AI**: Market sentiment and technical analysis
- **ccxt**: Unified exchange integration library
- **Schedule Library**: Task scheduling for automated trading
