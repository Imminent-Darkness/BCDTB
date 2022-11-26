# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 13:35:05 2022

@author: Dell
"""
import ccxt
import bybit
from settings import config
import schedule
import pandas as pd
import mplfinance as mpf
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import pandas_ta as ta
import warnings
import numpy as np
import time
from datetime import datetime
from pprint import pprint
import os
import glob

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')

class History:
    def __init__(self, exchange, symbol):
        self.exchange = exchange
        self.symbol = symbol

    def get_price_history(self, timeframe, since):
        from_ts = '2020-12-10 16:45:00'
        since = round(datetime.strptime(str(from_ts), '%Y-%m-%d %H:%M:%S').timestamp()*1000)
        #lastcandle = exchange.fetch_ohlcv(symbol,'1m',since=None,limit=1)
        #end = lastcandle[0]
        #endtime = end[0]
        bars = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=200)
        new_bars = bars.copy()
        loop_count = 0
        while len(new_bars) == 200:
            time.sleep(1)
            since = bars[-1][0]
            new_bars = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=200)
            bars.extend(new_bars)
            loop_count += 1
            if loop_count % 1000 == 0:
                    reached_timedate = pd.to_datetime(since, unit='ms')
                    print(f"Still fetching OHLCV data. Currently at {reached_timedate}")

            # status check for months in minutes
            '''
            month_in_minutes = 43200
            if bar_count % month_in_minutes == 0:
                print(f"{bar_count/month_in_minutes} months of candles downloaded...")
                '''


        df = pd.DataFrame(bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp')
        print(len(df))
        pprint(df.tail(10))
        print()
        pprint(df.head(10))
        os.makedirs('C:/Users/Dell/ccxt-bot/data', exist_ok=True)
        df.to_csv("C:/Users/Dell/ccxt-bot/data/btc-ohlcv-1m.csv")
        
        name = self.symbol.replace("/", "")
        parent_dir = os.getcwd()
        directory = "data"
        path = os.path.join(parent_dir, directory)
        directory = "historical-ohlcv-data"
        path = os.path.join(parent_dir, directory)
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory {path} created successfully")
        except OSError as error:
            print(f"Directory {path} cannot be created...")
            pprint(error)
        filepath = f"{path}/{name}-ohlcv.png"
        file = df.to_csv(filepath)
        
        return file, df