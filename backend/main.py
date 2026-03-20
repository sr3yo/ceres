from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os
import yfinance as yf
from datetime import datetime
from black_scholes import black_scholes, get_time_to_expiry

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() :
    return {"message": "Ceres API is running!!"}


#route to get prices 
@app.get("/price/{ticker}")
def getPrice(ticker : str):
    api_key = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

#route to get volatility for calculation later
@app.get("/yf/options/{ticker}")
def getYfOptions(ticker : str):
    stock = yf.Ticker(ticker)
    expiration_dates = stock.options
    chain = stock.option_chain(expiration_dates[0])
    calls = chain.calls.to_dict(orient="records")

    return{
        "expiration date": expiration_dates[0],
        "calls": calls
    }

@app.get("/analyze/{ticker}")
def analyze(ticker: str):
    # get stock price from polygon
    api_key = os.getenv("POLYGON_API_KEY")
    price_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
    price_response = requests.get(price_url)
    price_data = price_response.json()
    current_price = price_data["results"][0]["c"]

    # get options from yfinance
    stock = yf.Ticker(ticker)
    expiration_dates = stock.options
    
    # find first future expiration date
    today = datetime.today().strftime("%Y-%m-%d")
    future_dates = [d for d in expiration_dates if d > today]
    expiry = future_dates[0]
    
    chain = stock.option_chain(expiry)
    calls = chain.calls.to_dict(orient="records")

    results = []
    for contract in calls:
        strike = contract["strike"]
        market_premium = contract["lastPrice"]
        iv = contract["impliedVolatility"]

        T = get_time_to_expiry(expiry)
        
        if T > 0 and iv > 0:
            theoretical_price = black_scholes(current_price, strike, T, 0.05, iv)
            mispricing = round(market_premium - theoretical_price, 2)
            
            results.append({
                "contract": contract["contractSymbol"],
                "strike": strike,
                "market_premium": market_premium,
                "theoretical_price": theoretical_price,
                "mispricing": mispricing,
                "overpriced": bool(mispricing > 0)
            })

    return {
        "ticker": ticker,
        "current_price": current_price,
        "expiration_date": expiry,
        "contracts": results
    }