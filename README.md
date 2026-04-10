# Ceres

Ceres is a quantitative options analysis engine built in Python. It prices options contracts using the Black-Scholes model, compares theoretical prices against live market premiums to detect mispricing, and computes the full Greeks surface for any given ticker. A multi-agent layer built on LangGraph and the Claude API orchestrates analysis workflows and enforces structured outputs via Guardrails.

---

## What it actually does

Most retail options tools just show you the chain. Ceres tells you whether the market is pricing a contract correctly.

For any given ticker, Ceres:

1. Pulls the live stock price from Polygon.io and the full options chain from Yahoo Finance
2. Selects the nearest expiration 30+ days out to avoid theta decay noise near expiry
3. Runs every contract through Black-Scholes to compute a theoretical premium
4. Compares that theoretical price against the live market premium — the difference is the mispricing
5. Computes the four Greeks per contract
6. Scores each contract for liquidity based on bid-ask spread and open interest
7. Ranks all contracts by mispricing magnitude across 20 major tickers simultaneously

---

## Black-Scholes & Greeks

The core pricing model is Black-Scholes, which derives a theoretical option premium from five inputs: current stock price (S), strike price (K), time to expiration in years (T), risk-free rate (r), and implied volatility (σ).

The model computes two intermediate values — d1 and d2 — which feed into the cumulative normal distribution to produce the call or put price. Ceres uses the implied volatility directly from the live options chain rather than estimating it, which means the theoretical price reflects what the market *should* be pricing given its own volatility assumptions.

The Greeks tell you how sensitive a contract's price is to changes in each input:

- **Delta** — how much the option price moves per $1 move in the underlying. A call delta of 0.6 means the option gains ~$0.60 for every $1 the stock rises.
- **Gamma** — the rate of change of delta. High gamma means delta is unstable — the contract's sensitivity to price moves is itself changing rapidly. This matters most for contracts near the money close to expiry.
- **Theta** — daily time decay. A theta of -0.05 means the contract loses $0.05 in value per day purely from the passage of time, independent of price movement.
- **Vega** — sensitivity to changes in implied volatility. A vega of 0.10 means a 1% rise in IV adds $0.10 to the contract's value. This is the key input for the IV analysis routes.

---

## IV Analysis

Ceres computes a 30-day historical volatility (HV) from daily log returns, annualized using the standard √252 factor, and compares it against the median implied volatility from the live options chain.

The IV/HV ratio tells you whether options are cheap or expensive relative to realized volatility:
- **Ratio > 1.2** — options are expensive; the market is pricing in more volatility than has historically occurred
- **Ratio < 0.8** — options are cheap; IV is below realized volatility
- **Ratio ~1.0** — fairly priced

Ceres also computes an IV percentile over a 1-year rolling window — how often in the past year has IV been below its current level. High IV percentile means options are historically expensive right now.

---

## Opportunity Scanner

The scanner runs the full analysis pipeline across 20 tickers simultaneously and filters for contracts where the absolute mispricing exceeds $0.50 — filtering out noise from illiquid or near-worthless contracts. Results are sorted by mispricing magnitude and the top 10 are returned.

---

## Contract Quality Scoring

Not all mispriced contracts are tradeable. Ceres scores each contract for liquidity:

- **High** — bid-ask spread < 5% of ask price and open interest > 100
- **Medium** — spread < 15% and open interest > 10
- **Low** — everything else

Wide spreads mean you lose money just entering and exiting the trade, regardless of whether your pricing view is correct.

---

## Tech Stack

- **Python** — core language
- **FastAPI** — async REST API
- **LangGraph** — multi-agent orchestration
- **Claude API + Guardrails** — structured, schema-validated inference outputs with hallucination detection
- **Polygon.io** — real-time stock price data
- **yfinance** — options chain data
- **NumPy / SciPy** — Black-Scholes and Greeks computation
- **Pandas** — rolling volatility calculations

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /price/{ticker}` | Live stock price from Polygon.io |
| `GET /analyze/{ticker}` | Full options analysis — pricing, Greeks, mispricing for all contracts |
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
