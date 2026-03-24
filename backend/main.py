from itertools import chain

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os
import yfinance as yf
from datetime import datetime, timedelta
from black_scholes import black_scholes, get_time_to_expiry, calculate_greeks

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
    
    # find first future expiration date 30+ days out
    future_dates = [d for d in expiration_dates if d > (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")]
    expiry = future_dates[0]
    
    chain = stock.option_chain(expiry)
    calls = chain.calls.to_dict(orient="records")
    puts = chain.puts.to_dict(orient="records")

    # run black scholes on calls
    call_results = []
    for contract in calls:
        strike = contract["strike"]
        market_premium = contract["lastPrice"]
        iv = contract["impliedVolatility"]
        T = get_time_to_expiry(expiry)
        
        if T > 0 and iv > 0:
            theoretical_price = black_scholes(current_price, strike, T, 0.05, iv, "call")
            mispricing = round(market_premium - theoretical_price, 2)
            greeks = calculate_greeks(current_price, strike, T, 0.05, iv, "call")
            
            call_results.append({
                "contract": contract["contractSymbol"],
                "type": "call",
                "strike": strike,
                "market_premium": market_premium,
                "theoretical_price": theoretical_price,
                "mispricing": mispricing,
                "overpriced": bool(mispricing > 0),
                "greeks": greeks
            })

    # run black scholes on puts
    put_results = []
    for contract in puts:
        strike = contract["strike"]
        market_premium = contract["lastPrice"]
        iv = contract["impliedVolatility"]
        T = get_time_to_expiry(expiry)
        
        if T > 0 and iv > 0:
            theoretical_price = black_scholes(current_price, strike, T, 0.05, iv, "put")
            mispricing = round(market_premium - theoretical_price, 2)
            greeks = calculate_greeks(current_price, strike, T, 0.05, iv, "put")
            
            put_results.append({
                "contract": contract["contractSymbol"],
                "type": "put",
                "strike": strike,
                "market_premium": market_premium,
                "theoretical_price": theoretical_price,
                "mispricing": mispricing,
                "overpriced": bool(mispricing > 0),
                "greeks": greeks
            })
    hist = stock.history(period="30d")
    hist["returns"] = hist["Close"].pct_change()
    hv = hist["returns"].std() * (252 ** 0.5)

    put_volume = chain.puts["volume"].sum()
    call_volume = chain.calls["volume"].sum()
    pcr = round(put_volume / call_volume, 2) if call_volume > 0 else 0





    return {
    "ticker": ticker,
    "current_price": current_price,
    "expiration_date": expiry,
    "historical_volatility": round(float(hv), 4),
    "put_call_ratio": float(pcr),
    "market_sentiment": "bearish" if pcr > 1 else "bullish",
    "calls": call_results,
    "puts": put_results
}


@app.get("/volatility/{ticker}")
def get_historical_volatility(ticker: str):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="30d")
    
    # calculate daily returns
    hist["returns"] = hist["Close"].pct_change()
    
    # annualized historical volatility
    hv = hist["returns"].std() * (252 ** 0.5)
    
    # put/call ratio
    expiration_dates = stock.options
    future_dates = [d for d in expiration_dates if d > (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")]
    expiry = future_dates[0]
    chain = stock.option_chain(expiry)
    
    put_volume = chain.puts["volume"].sum()
    call_volume = chain.calls["volume"].sum()
    pcr = round(put_volume / call_volume, 2) if call_volume > 0 else 0
    
    return {
        "ticker": ticker,
        "historical_volatility_30d": round(float(hv), 4),
        "put_call_ratio": float(pcr),
        "interpretation": "bearish" if pcr > 1 else "bullish"
    }

@app.get("/iv-analysis/{ticker}")
def get_iv_analysis(ticker: str):
    stock = yf.Ticker(ticker)
    
    # getting 1 year of historical data
    hist = stock.history(period="1y")
    hist["returns"] = hist["Close"].pct_change()
    
    # 30 day data
    hv_30 = hist["returns"].tail(30).std() * (252 ** 0.5)
    
    # calculate rolling 30day HV for entire year for percentile
    rolling_hv = hist["returns"].rolling(30).std() * (252 ** 0.5)
    
    # IV from options
    expiration_dates = stock.options
    future_dates = [d for d in expiration_dates if d > (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")]
    expiry = future_dates[0]
    chain = stock.option_chain(expiry)
    
    
    avg_iv = chain.calls["impliedVolatility"].median()
    
    
    iv_percentile = round(float((rolling_hv < avg_iv).sum() / len(rolling_hv.dropna()) * 100), 2)
    
    # comparing IV and HV
    iv_hv_ratio = round(float(avg_iv / hv_30), 2)
    
    if iv_hv_ratio > 1.2:
        iv_interpretation = "options are expensive — IV significantly above HV"
    elif iv_hv_ratio < 0.8:
        iv_interpretation = "options are cheap — IV significantly below HV"
    else:
        iv_interpretation = "options are fairly priced — IV close to HV"
    
    return {
        "ticker": ticker,
        "current_iv": round(float(avg_iv), 4),
        "historical_volatility_30d": round(float(hv_30), 4),
        "iv_hv_ratio": iv_hv_ratio,
        "iv_percentile": iv_percentile,
        "interpretation": iv_interpretation
    }