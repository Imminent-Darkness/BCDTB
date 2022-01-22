import ccxt
import bybit
import config
import schedule
import pandas as pd

pd.set_option('display.max_rows', None)

import warnings

warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time

exchange = ccxt.bybit({
    "apiKey": config.TESTNET_BYBIT_API_KEY,
    "secret": config.TESTNET_BYBIT_SECRET_KEY,
    'enableRateLimit': True,
})

symbol = 'BTC/USD'
amount = 10.0
leverage = 5

exchange.set_sandbox_mode(True)

markets = exchange.load_markets()

exchange_props = exchange.has
for prop in exchange_props:
    print(prop)
from pprint import pprint
pprint(exchange.fetch_balance())

position_df = pd.DataFrame(
 index=markets, columns=['in_position', 'in_short_position', 'in_long_position', 'order_id', 'stop_id', 'qty', 'base_price', 'stop_px'],
)

for i in position_df.index:
    position_df.at[i, 'in_position'] = False 
    position_df.at[i, 'in_short_position'] = False 
    position_df.at[i, 'in_long_position'] = False
    position_df.at[i, 'order_id'] = " "
    position_df.at[i, 'stop_id'] = " "
    position_df.at[i, 'qty'] = 0
    position_df.at[i, 'base_price'] = 0
    position_df.at[i, 'stop_px'] = 0

print(position_df)

# Moving Average
def ma(Data, period, onwhat, where):
    
    for i in range(len(Data)):
            try:
                Data[i, where] = (Data[i - period:i + 1, onwhat].mean())
        
            except IndexError:
                pass
    return Data

# Exponential Moving Average
def ema(Data, alpha, window, what, whereSMA, whereEMA):
    
    # alpha is the smoothing factor
    # window is the lookback period
    # what is the column that needs to have its average calculated
    # where is where to put the exponential moving average
    
    alpha = alpha / (window + 1.0)
    beta  = 1 - alpha
    
    # First value is a simple SMA
    Data[window - 1, whereSMA] = np.mean(Data[:window - 1, what])
    
    # Calculating first EMA
    Data[window, whereEMA] = (Data[window, what] * alpha) + (Data[window - 1, whereSMA] * beta)
# Calculating the rest of EMA
    for i in range(window + 1, len(Data)):
            try:
                Data[i, whereEMA] = (Data[i, what] * alpha) + (Data[i - 1, whereEMA] * beta)
        
            except IndexError:
                pass
    return Data

# Weighted Moving Average
def wma(df, column='close', n=193, add_col=False):

    weights = np.arange(1, n + 1)
    wmas = df[column].rolling(n).apply(lambda x: np.dot(x, weights) /
                                       weights.sum(), raw=True).to_list()

    if add_col == True:
        df[f'{column}_WMA_{n}'] = wmas
        return df
    else:
        return wmas

# Linear-weighted moving average
def lwma(Data, period):
    weighted = []
    for i in range(len(Data)):
            try:
                total = np.arange(1, period + 1, 1) # weight matrix
                
                matrix = Data[i - period + 1: i + 1, 3:4]
                matrix = np.ndarray.flatten(matrix)
                matrix = total * matrix # multiplication
                wma = (matrix.sum()) / (total.sum()) # WMA
                weighted = np.append(weighted, wma) # add to array
            except ValueError:
                pass
    return weighted


def tr(data):
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['low-pc'] = abs(data['low'] - data['previous_close'])

    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr


def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr


def supertrend(df, period=7, atr_multiplier=3):
    hl2 = (df['high'] + df['low']) / 2
    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (atr_multiplier * df['atr'])
    df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df


def close_position(side: str):

    type = 'market'
    price = None

    print('closing open position')
    pprint(exchange.create_order(symbol, type, side, amount, price, {
        'reduce_only': True, 'close_on_trigger': True
    }))

def long(sym: str, amnt: float, leverage: int):
    # SELL ORDER 2
    symbol = sym
    type = 'market'
    side = 'buy'
    amount = amnt
    price = None
    try:
        exchange.set_leverage(leverage, symbol, {'buy_leverage': leverage, 'sell_leverage': leverage})
    except Exception:
        pass

    last_ticker = exchange.fetch_ticker(symbol)
    last_price = last_ticker['last']

    print("last price is:")
    print(last_price)
    safety_margin = last_price - (last_price * 0.025)
    print("safety margin is:")
    print(safety_margin)

    order = exchange.create_order(symbol, type, side, amount, price, {
        'qty': amount, 'basePrice': last_price, 'stopPx': safety_margin
    })
    print("******* BUY ORDER ********")
    pprint(order)
    
    position_df['in_position'][symbol]=True
    position_df['in_short_position'][symbol]=False
    position_df['in_long_position'][symbol]=True
    position_df['order_id'][symbol]=order['id']

    print("************************ POSITION_DF ****************************")
    pprint(position_df)
    
    return order

#############################################################################
#############################################################################

# SHORT

def short(sym: str, amnt: float, leverage: int):
    # SELL ORDER 2
    symbol = sym
    type = 'market'
    side = 'sell'
    amount = amnt
    price = None
    try:
        exchange.set_leverage(leverage, symbol, {'buy_leverage': leverage, 'sell_leverage': leverage})
    except Exception:
        pass

    last_ticker = exchange.fetch_ticker(symbol)
    last_price = last_ticker['last']

    print("last price is:")
    print(last_price)
    safety_margin = last_price + (last_price * 0.025)
    print("safety margin is:")
    print(safety_margin)

    order = exchange.create_order(symbol, type, side, amount, price, {
        'qty': amount, 'basePrice': last_price, 'stopPx': safety_margin
    })
    print("******* SELL ORDER ********")
    pprint(order)
    
    position_df['in_position'][symbol]=True
    position_df['in_short_position'][symbol]=True
    position_df['in_long_position'][symbol]=False
    position_df['order_id'][symbol]=order['id']
    position_df['qty'][symbol]=amount
    position_df['base_price'][symbol]=last_price
    position_df['stop_px'][symbol]=safety_margin

    print("************************ POSITION_DF ****************************")
    pprint(position_df)
    
    return order


def check_buy_sell_signals(df: object, symbol: str, amount: float, leverage: int, macro: bool):

    print("checking for buy and sell signals")
    print(df.tail(5))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1
    
    in_pos = position_df.at[symbol, 'in_position']
    in_long = position_df.at[symbol, 'in_long_position']
    in_short = position_df.at[symbol, 'in_short_position']
    print("in_pos = " + str(in_pos))
    print("in_long = " + str(in_long))
    print("in_short = " + str(in_short))
    
    last_ticker = exchange.fetch_ticker(symbol)
    last_px = last_ticker['last']

    print('Checking if in micro uptrend...')
    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("changed to uptrend, buy if price is above wma")
        if in_short == True:
            print("closing short position")
            exchange.cancel_order(position_df['stop_id'][symbol], symbol)
            close_position('buy')
            position_df['in_short_position'][symbol] = False
            position_df['in_position'][symbol] = False
            
            
            position_df['in_short_position'][symbol] = False
        if in_pos == False:
            if macro:
                print("creating long position")
                long(sym=symbol, amnt=amount, leverage=leverage)
                position_df['in_long_position'][symbol] = True
                position_df['in_short_position'][symbol] = False
                position_df['in_position'][symbol] = True
        else:
            print("either the price is not above the weighted moving average")
            print(" or we are already in position")

            # def edit_order(self, id, symbol, type, side, amount=None, price=None, params={}):

            # edit stop order


    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        print("changed to downtrend, sell")
        if in_long == True:
            print("closing long position")
            exchange.cancel_order(position_df['stop_id'][symbol], symbol)
            close_position('sell')
            position_df['in_long_position'][symbol] = False
            position_df['in_position'][symbol] = False
        if in_pos == False:
            if not macro:
                print("creating short position")
                short(sym=symbol, amnt=amount, leverage=leverage)
                position_df['in_long_position'][symbol] = False
                position_df['in_short_position'][symbol] = True
                position_df['in_position'][symbol] = True
        else:
            print("either the price is not below the weighted moving average")
            print("or we are already in position")

            # edit stop order

            # edit stop order            



#############################################################################
#############################################################################


def run_bot():

#    symbol = 'BTC/USD'
#    amount = 10
#    leverage = 5
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=200)
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    my_wma = wma(df)
    [float(i) for i in my_wma]
    my_wma = my_wma[:-1]
    last_wma = my_wma[-1:][0]
    last_ticker = exchange.fetch_ticker(symbol)
    last_px = last_ticker['last']
    print('my_wma:')
    pprint(my_wma)
    print()
    print('last_wma')
    pprint(last_wma)
    print()
    print('last_ticker:')
    pprint(last_ticker)
    print()
    print('last_price:')
    pprint(last_px)



    macroUP = last_px > last_wma

    supertrend_data = supertrend(df)

    check_buy_sell_signals(supertrend_data, symbol, amount, leverage, macroUP)
#    ccxt.bybit.create_buy_seller

schedule.every(10).seconds.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)






'''
WORKING SHORT ORDER WITH MODIFIABLE STOPLOSS
'''
'''
# SELL ORDER 2
symbol = 'BTC/USD'
type = 'market'
side = 'sell'
amount = 5
price = None


last_ticker = exchange.fetch_ticker(symbol)
last_price = last_ticker['last']

print("last price is:")
print(last_price)
safety_margin = last_price + (last_price * 0.005)
print("safety margin is:")
print(safety_margin)

#position_df{['symbol', 'in_position', 'in_short_position', 'in_long_position', 'order_id', 'stop_id']}
order = exchange.create_order(symbol, type, side, amount, price, {
    'qty': amount
})
print("******* SELL ORDER ********")
pprint(order)

# STOP-LOSS FOR SELL ORDER
side = 'buy'
price = safety_margin

stop_order = exchange.create_order(symbol, type, side, amount, price, {
    'qty': amount, 'base_price': last_price, 'stop_px': safety_margin, 'close_on_trigger': True
})

print("******** STOP LOSS FOR SELL ORDER ********")
pprint(stop_order)

#position_df['in_position'] = position_df['in_position'].replace(['Blue','Red'],'Green')
position_df['in_position'][symbol]=True
position_df['in_short_position'][symbol]=True
position_df['in_long_position'][symbol]=False
position_df['order_id'][symbol]=order['id']
position_df['stop_id'][symbol]=stop_order['id']
print("************************ POSITION_DF ****************************")
pprint(position_df)

'''