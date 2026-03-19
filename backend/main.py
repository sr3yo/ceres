from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os
import yfinance as yf

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



@app.get("/price/{ticker}")
def getPrice(ticker : str):
    api_key = os.getenv("POLYGON_API_KEY")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

@app.get("/yf/options/{ticker}")
def getYfOptions(ticker : str):
    stock = yf.Ticker(ticker)
    expiration_dates = stock.options
    
    # get options chain for first expiration date
    chain = stock.option_chain(expiration_dates[0])
    
    # get calls
    calls = chain.calls.to_dict(orient="records")

    return{
        "expiration date": expiration_dates[0],
        "calls": calls[:5]
    }

    