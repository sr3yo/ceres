#to compute black scholes 

import numpy as np
from scipy.stats import norm
from datetime import datetime

def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    S = current stock price
    K = strike price
    T = time to expiration (in years)
    r = risk free interest rate (use 0.05 for 5%)
    sigma = implied volatility
    option_type = "call" or "put"
    """
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return round(price, 2)

def get_time_to_expiry(expiration_date: str) -> float:
    today = datetime.today()
    expiry = datetime.strptime(expiration_date, "%Y-%m-%d")
    days = (expiry - today).days
    return days / 365


def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    """
    Calculate all 4 Greeks for an option
    S = current stock price
    K = strike price
    T = time to expiration (in years)
    r = risk free rate
    sigma = implied volatility
    """
    
    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # delta
    if option_type == "call":
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1
    
    # gamma (same for calls and puts)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # theta
    if option_type == "call":
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    # vega (same for calls and puts)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    return {
        "delta": round(float(delta), 4),
        "gamma": round(float(gamma), 4),
        "theta": round(float(theta), 4),
        "vega": round(float(vega), 4)
    }