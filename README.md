# Ceres

Ceres is a quantitative options analysis engine built in Python. It prices options contracts using Black-Scholes, compares theoretical prices against live market premiums to find mispricing, and computes the full Greeks for any ticker. We also built a multi-agent layer using LangGraph and the Claude API to orchestrate analysis workflows with structured, validated outputs.

We built this because most retail options tools just show you the chain. We wanted something that actually tells you whether the market is pricing a contract correctly or not.

---

## What it does

For any given ticker, Ceres:

1. Pulls the live stock price from Polygon.io and the full options chain from Yahoo Finance
2. Selects the nearest expiration 30+ days out to avoid noise from contracts about to expire
3. Runs every contract through Black-Scholes to get a theoretical fair price
4. Compares that price against the real market premium to find mispricing
5. Computes the four Greeks per contract
6. Scores each contract for how tradeable it actually is based on liquidity
7. Scans 20 major tickers at once and ranks everything by mispricing size

---

## Black-Scholes and Greeks

We want to be upfront: we are not quant experts. We learned this from documentation and research papers and implemented it ourselves.

Black-Scholes takes five inputs to compute a theoretical option price: current stock price (S), strike price (K), time to expiration in years (T), risk-free rate (r), and implied volatility (sigma). From these it computes d1 and d2, which feed into the normal distribution to give you the call or put premium.

One important detail: Ceres uses the implied volatility directly from the live options chain rather than estimating it. This means the theoretical price is based on what the market itself believes volatility will be, so any mispricing you find is a genuine discrepancy in how the contract is priced.

The Greeks measure how sensitive the option price is to changes in each of these inputs:

- **Delta** measures how much the option price changes for every $1 move in the stock. A call with delta 0.6 gains about $0.60 when the stock goes up $1.
- **Gamma** measures how fast delta itself is changing. When gamma is high, the option's sensitivity to price moves is shifting quickly. This is most relevant for contracts that are close to the strike price and close to expiration.
- **Theta** is the daily cost of holding an option. A theta of -0.05 means the contract loses $0.05 every single day just from time passing, even if the stock price does not move at all.
- **Vega** measures how much the option price changes when implied volatility moves by 1%. A vega of 0.10 means a 1% rise in IV adds $0.10 to the contract value. This is what makes the IV analysis section useful.

---

## IV Analysis

Ceres calculates 30-day historical volatility from daily returns, annualized with the standard square root of 252 factor, and compares it against the median implied volatility from the options chain.

The ratio between IV and HV tells you whether options are cheap or expensive right now:
- Ratio above 1.2 means options are expensive. The market expects more volatility than has actually happened historically.
- Ratio below 0.8 means options are cheap. IV is lower than realized volatility.
- Ratio around 1.0 means contracts are fairly priced.

We also compute an IV percentile over the past year so you can see how current IV compares to its own history. A high IV percentile means options are expensive by historical standards for that ticker.

---

## Opportunity Scanner

The scanner runs the full pipeline across 20 tickers at the same time and filters for contracts where the mispricing is larger than $0.50. This removes noise from tiny or illiquid contracts. Everything is sorted by mispricing size and the top 10 opportunities are returned.

---

## Contract Quality Scoring

Finding a mispriced contract does not mean you can actually trade it profitably. Ceres scores each contract for liquidity:

- **High**: bid-ask spread is less than 5% of the ask price, and open interest is above 100
- **Medium**: spread under 15% and open interest above 10
- **Low**: everything else

A wide bid-ask spread means you lose money just getting in and out of the trade, regardless of whether your analysis is right.

---

## Tech Stack

- **Python** for everything
- **FastAPI** for the async REST API
- **LangGraph** for multi-agent orchestration
- **Claude API + Guardrails** for structured outputs and hallucination detection
- **Polygon.io** for real-time stock prices
- **yfinance** for options chain data
- **NumPy / SciPy** for Black-Scholes and Greeks
- **Pandas** for rolling volatility calculations

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /price/{ticker}` | Live stock price from Polygon.io |
| `GET /analyze/{ticker}` | Full analysis: pricing, Greeks, mispricing for all contracts |
| `GET /volatility/{ticker}` | 30-day HV, put/call ratio, market sentiment |
| `GET /iv-analysis/{ticker}` | IV vs HV ratio, IV percentile, pricing interpretation |
| `GET /contract-quality/{ticker}` | Liquidity scoring for all contracts |
| `GET /analyze/multiple/{tickers}` | Batch analysis across comma-separated tickers |
| `GET /scanner` | Top mispriced contracts across 20 major tickers |

---

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

Run the server:
```bash
uvicorn backend.main:app --reload
```
