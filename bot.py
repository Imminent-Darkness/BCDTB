# -*- coding: utf-8 -*-
"""
Steven Wilkins
CS401-Capstone Project

Python class description:   myasset.py creates a dedicated object for each traded
                            currency pair. This object provides the means for the
                            main program to fetch price data associated with the
                            pair from the exchange, use a technical analysis 
                            strategy to detect buy and sell signals, enter long
                            and short leveraged positions trading that pair, and
                            properly close those positions.
"""
#import logging
#logging.basicConfig(level=logging.DEBUG)

from settings import config
from python import myasset
import ccxt
import schedule
import pandas as pd
import warnings
import time

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')


def set_exchange(attempt=0):
    attempt = attempt + 1
    if attempt > 5:
        print('Unable to connect to bybit')
        raise SystemExit
    try:
        exchange = ccxt.bybit({
            'options': {
                'adjustForTimeDifference': True,
                },
            "apiKey": config.API_KEY,
            "secret": config.SECRET_KEY,
            'enableRateLimit': True
        })
        exchange.set_sandbox_mode(config.SANDBOX)
    except ccxt.NetworkError as e:
        print('Connection to bybit failed due to a network error:', str(e))
        set_exchange(attempt)
    except Exception as e:
        print('Connection to bybit failed with:', str(e))
        set_exchange(attempt)
    return exchange


def prepare_assets(exchange,symbol, timeframe, amount, leverage, stoploss, takeprofit, attempt=0):
    attempt = attempt + 1
    if attempt > 5:
        print('Unable to prepare assets')
        raise SystemExit
    assets = []
    try:
        if type(symbol) == str:
            if symbol == 'USDT':
                markets = exchange.load_markets()
                for m in markets:
                    if m.endswith('USDT'):
                        assets.append(myasset.Myasset(exchange,symbol, timeframe, amount, leverage, stoploss, takeprofit))
            else:
                assets.append(myasset.Myasset(exchange,symbol, timeframe, amount, leverage, stoploss, takeprofit))
        else:
            for s in symbol:
                assets.append(myasset.Myasset(exchange,symbol, timeframe, amount, leverage, stoploss, takeprofit))
    except Exception as e:
        print(f'Preparing assets failed with {e}')
        prepare_assets(exchange ,symbol, timeframe, amount, leverage, stoploss, takeprofit, attempt)
    return assets


def set_leverage(exchange, symbol, leverage):
    try:
        print(f"Setting leverage for {symbol} to {leverage}...")
        exchange.set_leverage(leverage, symbol, {'buy_leverage': leverage, 'sell_leverage': leverage})
        print(f"Leverage for {symbol} has been successfully set.")
    except Exception:
        print(f"Leverage for {symbol} is already set to {leverage}.")
        pass


# Set variables from config.py

symbol = config.SYMBOL
timeframe = config.TIME_FRAME
amount = config.AMOUNT
leverage = config.LEVERAGE
stoploss = config.STOP_LOSS
takeprofit = config.TAKE_PROFIT


# Connect to exchange and prepare assets 

exchange = set_exchange()
assets = prepare_assets(exchange, symbol, timeframe, amount, leverage, stoploss, takeprofit)

for asset in assets:
    set_leverage(exchange, symbol, leverage)
    print(repr(asset))


def run_bot():
    global assets
    
    for a in assets:
        a.run_bot()
        time.sleep(2)

schedule.every(10).seconds.do(run_bot)

while True:

    schedule.run_pending()
    time.sleep(1)
