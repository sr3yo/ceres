# Ceres

A Python-based quantitative options analysis system that combines real-time market data, Black-Scholes pricing, and multi-agent AI orchestration to identify mispricings and evaluate options contracts across major equities.
WORKING ON GETTING IT DEPLOYED!

## Overview

Ceres ingests live market data from Polygon.io and Yahoo Finance, runs Black-Scholes theoretical pricing against real market premiums, calculates options Greeks, and surfaces mispriced contracts ranked by magnitude. A FastAPI backend exposes all analysis as low-latency REST endpoints, with a LangGraph multi-agent layer and Claude API integration for structured, schema-validated inference outputs.

## Features

- **Black-Scholes Pricing** — Computes theoretical call and put premiums and compares against live market prices to detect mispricing
- **Greeks Calculation** — Calculates Delta, Gamma, Theta, and Vega for all contracts
- **IV Analysis** — Compares implied volatility against 30-day historical volatility, computes IV percentile over a 1-year rolling window
- **Contract Quality Scoring** — Scores contracts as high/medium/low liquidity based on bid-ask spread percentage and open interest
- **Put/Call Ratio & Sentiment** — Derives market sentiment signals from options volume
- **Opportunity Scanner** — Scans 20 major tickers simultaneously, filters for significant mispricings (> $0.50), and returns top opportunities ranked by mispricing magnitude
- **Multi-ticker Analysis** — Batch analysis across multiple tickers in a single request
- **Claude API + Guardrails** — Detects hallucinations and enforces schema-validated structured outputs across agent workflows

## Tech Stack

- **Python** — Core language
- **FastAPI** — Async REST API layer
- **LangGraph** — Multi-agent orchestration
- **Claude API** — LLM inference with Guardrails for structured output validation
- **Polygon.io** — Real-time stock price data
- **yfinance** — Options chain data
- **NumPy / SciPy** — Black-Scholes and Greeks computation
- **Pandas** — Historical volatility and rolling calculations

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /price/{ticker}` | Live stock price from Polygon.io |
| `GET /analyze/{ticker}` | Full options analysis — pricing, Greeks, mispricing |
| `GET /volatility/{ticker}` | 30-day historical volatility and put/call ratio |
| `GET /iv-analysis/{ticker}` | IV vs HV comparison, IV percentile, pricing interpretation |
| `GET /contract-quality/{ticker}` | Liquidity scoring for all contracts |
| `GET /analyze/multiple/{tickers}` | Batch analysis across comma-separated tickers |
| `GET /scanner` | Scans 20 major tickers for top mispriced contracts |

## Setup

```bash
git clone https://github.com/sr3yo/ceres.git
cd ceres
pip install -r requirements.txt
```

Create a `.env` file:
```
POLYGON_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Run the API:
```bash
uvicorn backend.main:app --reload
```

## Example

```bash
# Analyze AAPL options
GET /analyze/AAPL

# Scan for top mispriced contracts across 20 tickers
GET /scanner
```

## How It Works

1. Fetches the current stock price from Polygon.io
2. Pulls the nearest options chain 30+ days out from Yahoo Finance
3. Runs Black-Scholes against every contract using implied volatility from the chain
4. Computes mispricing as `market_premium - theoretical_price`
5. Calculates Greeks (Delta, Gamma, Theta, Vega) per contract
6. Scores contract liquidity based on bid-ask spread and open interest
7. Surfaces the most mispriced contracts, ranked by absolute mispricing value
8. Claude API layer validates and structures agent outputs via Guardrails
