<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cryptocurrency trading bot repository that implements automated trading strategies using AI analysis. The bot primarily trades BTC/USDT futures contracts on WEEX and OKX exchanges, with market analysis powered by DeepSeek AI.

## Environment Setup

### Required Dependencies
All dependencies are listed in `requirements.txt`:
- ccxt (exchange integration)
- requests, urllib3 (HTTP requests)
- pandas (data analysis)
- openai (DeepSeek AI integration)
- python-dotenv (environment variable management)
- schedule (task scheduling)

### Environment Variables
Create a `.env` file in the project root with the following variables:
- `DEEPSEEK_API_KEY` - DeepSeek AI API key
- `WEEX_API_KEY` - WEEX exchange API key
- `WEEX_API_SECRET` or `WEEX_SECRET` - WEEX exchange secret
- `WEEX_ACCESS_PASSPHRASE` - WEEX passphrase
- `OKX_API_KEY` - OKX exchange API key
- `OKX_SECRET` - OKX exchange secret
- `OKX_PASSWORD` - OKX trading password

Reference `.env.example` for the complete template.

## Core Architecture

### Main SDK: weex_sdk.py (56KB)
The central `WeexClient` class provides all WEEX exchange integration:
- Authentication and API request signing
- Order management (create_market_order, place_order)
- Position querying (fetch_positions)
- Market data (fetch_ohlcv for K-line data)
- History orders (get_order_history, get_history_plan_orders)
- Leverage configuration (set_leverage)

Key methods:
- `_sign()` - HMAC-SHA256 signature generation with BASE64 encoding
- `_request()` - HTTP request handler with authentication headers

### Strategy Files (Main Trading Bots)
1. **deepseek_ok_带市场情绪+指标版本.py** - Primary strategy using OKX exchange with market sentiment and technical indicators
2. **deepseek_ok_带指标plus版本.py** - Enhanced version with additional indicators
3. **deepseek_weex1.py** - WEEX-specific strategy implementation
4. **deepseek_weex.py** - Older WEEX strategy version

All strategy files follow this pattern:
- Initialize DeepSeek AI client and exchange connection
- Load configuration (TRADE_CONFIG dict)
- Define data collection functions (OHLCV, indicators)
- Implement AI analysis with prompt engineering
- Execute trades based on AI decisions

### Utility Scripts

**Position Management:**
- `close_btc_long.py` - Close BTC long positions on WEEX
- `close_all_positions.py` - Close all open positions
- `get_current_positions.py` - Fetch and display current positions
- `open_btc_long_script.py` - Open BTC long position with preset parameters

**Account & Order Management:**
- `get_account_assets.py` - Retrieve account balance and asset info
- `fetch_order_history.py` - Retrieve order history with profit calculation
- `query_history_orders.py` - Query historical orders with formatting
- `open_long_position.py` - Generic long position opener

**Market Data:**
- `fetch_kline_15min.py` - Fetch 15-minute K-line data from WEEX

### Testing Suite
Multiple test files in the root directory:
- `test_weex*.py` - WEEX SDK integration tests
- `test_market_order*.py` - Market order execution tests
- `test_leverage*.py` - Leverage configuration tests
- `test_get_account_assets.py` - Account asset retrieval tests

### Script Execution Framework: run_script_selector.py
Central script runner that:
- Parses `SCRIPT.md` for command definitions
- Executes shell commands stored in markdown code blocks
- Provides a unified interface to run common operations

## Common Operations

### Running Scripts
1. **Using script selector (recommended):**
   ```bash
   python3 run_script_selector.py
   ```
   This reads `SCRIPT.md` and presents a menu of available commands.

2. **Direct execution:**
   ```bash
   # With uv package manager
   uv run python3 get_account_assets.py

   # Or directly with python
   python3 close_btc_long.py
   ```

### Available Commands (from SCRIPT.md)
- Get account assets: `uv run python3 get_account_assets.py`
- Get current positions: `uv run python3 get_current_positions.py`
- Query order history: `uv run python3 query_history_orders.py`

### Testing
Each component has dedicated test files. Run individual test files directly:
```bash
python3 test_weex.py
python3 test_market_order.py
python3 test_leverage.py
```

### Development
1. **Modifying strategies:** Edit the main strategy files (deepseek_*.py)
2. **Adding utilities:** Create new Python scripts following existing patterns
3. **Updating SDK:** Modify `weex_sdk.py` for new exchange API features
4. **Configuration:** All trading parameters are in `TRADE_CONFIG` dicts within each strategy

## Key Configuration Parameters

Most strategy files use a `TRADE_CONFIG` dict with these common keys:
- `symbol` - Trading pair (e.g., 'cmt_btcusdt' for WEEX, 'BTC/USDT:USDT' for OKX)
- `leverage` - Leverage multiplier (typically 10x)
- `timeframe` - K-line timeframe (typically '15m')
- `amount` - Position size in base currency
- `test_mode` - Whether to run in simulation mode

## Recent Changes (Git History)
- Added script selector tool for parsing SCRIPT.md commands
- Implemented profit display for order history queries
- Added history orders API implementation
- Fixed API signature alignment with official demo
- Refactored timestamp formatting in various scripts

## Important Notes

1. **Position Direction:** This codebase implements **unidirectional positions only** (not hedging)
2. **Exchange Integration:** WEEX SDK in `weex_sdk.py` follows official API documentation (see DOC.md)
3. **API Documentation:** Full API reference in `DOC.md` with curl examples
4. **Market Analysis:** Uses DeepSeek AI for market sentiment and technical indicator analysis
5. **Risk Management:** Includes stop-loss and take-profit parameters in order placement

## Repository Structure
```
├── weex_sdk.py                 # Core exchange SDK (56KB)
├── deepseek_*.py              # Main strategy files
├── close_btc_long.py          # Position closing utilities
├── get_account_assets.py      # Account queries
├── get_current_positions.py   # Position queries
├── query_history_orders.py    # Order history
├── fetch_kline_15min.py       # Market data
├── run_script_selector.py     # Script execution framework
├── SCRIPT.md                  # Command definitions
├── DOC.md                     # API documentation
├── test_*.py                  # Test suite
├── requirements.txt           # Dependencies
├── .env                       # Configuration (not in repo)
└── .env.example              # Config template
```

## Getting Started

1. Copy `.env.example` to `.env` and fill in API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Review available commands: `python3 run_script_selector.py`
4. Run strategy: `python3 deepseek_weex1.py` (or any strategy file)
5. Monitor positions: `python3 get_current_positions.py`
