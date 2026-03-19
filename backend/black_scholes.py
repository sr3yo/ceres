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