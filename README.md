# Bybit Cryptocurrency Derivatives Trading Bot 

The Bybit Cryptocurrency Derivatives Trading Bot (BCDTB) automates the trading 
of cryptocurrency derivatives on the Bybit exchange. This is done by regularly 
fetching OHLCV (Open, High, Low, Close, Volume) data directly from Bybit and 
generating buy/sell signals using a trading strategy[^1] based on technical 
analysis. This strategy uses three Supertrend instances, the 50_EMA, and 
200_EMA to determine trend direction while using the Stochastic RSI for entries.



## The Strategy 

### The 50_EMA and 200_EMA

The strategy implemented in the BCDTB determines the macro trend of the OHLCV
data by looking at the two exponential moving averages. If the 50_EMA is above
the 200_EMA, then the price is in a macro uptrend. If the 50_EMA is below the 
200_EMA, then the price is in a macro downtrend. The BCDTB will only look for 
long positions when in a macro uptrend, otherwise it will look for short 
positions when the macro trend is down. 

### Supertrend 

Three Supertrend[^2] instances are used to determine when a micro trend occurs 
in the same direction as the macro trend. The first supertrend is instantiated 
with (period=10, atr_multiplier=1), the second with (period=11, atr_multiplier=2), 
and the third with (period=12, atr_multiplier=3). If two supertrends are 
indicating the same direction as the EMAs, the BCDTB will look for entry signals
from the Stochastic RSI.

### Stochastic RSI 

If the price is determined to be in both a macro and micro uptrend, a long 
position will be created when SD is below 20 and K is crossing up over D. 
Alternatively, if the price is determined to be in both a macro and micro 
downtrend, a short position is created when the SD is above 80 and K is crossing 
below D.

## How to Use 

## Bybit Account 

To use the BCDTB, the trader will need a Bybit account with cryptocurrency in
their derivatives wallet. First they will have to deposit the cryptocurrency into 
the corresponding spot wallet, then transfer it into the derivatives wallet. If 
the cryptocurrency is anything other than USDT, they will be confined to trading
that cryptocurrency only against USD (ex. BTC/USD, ETH/USD, etc.). If the trader
would prefer to have fast access to a variety of trading pairs, it would be 
beneficial to exchange their cryptocurrency for USDT, which will trade against 
all available cryptocurrencies (ex. BTC/USDT, ETH/USDT, XRP/USDT, etc.).

## Bybit API Key 

Once the Trader's Bybit account is set-up, they need to go into their account
settings and generate an API Key. Give the API all permissions except for 
withdrawal. If the BCDTB is going to be running on a specific server with a 
static IP address, the Trader can restrict the API to only work with that IP 
address, which is more secure. If this is not the case, or the Trader is unsure,
then give the API permission to run from anywhere. The Trader needs to pay 
attention and write the API secret down immediately after creating it, because 
it will only be displayed at that time.

## Configure BCDTB Settings 

Settings must be configured in a file named config.py, which is located in the 
settings folder of the project directory ( ~/BCDTB/settings/config.py ). 
Examples of how to do this are presented below.

### Set API Key and Secret 

```python
API_KEY = 'your-api-key'
SECRET_KEY = 'your-api-secret'

```

### Live Exchange or Testnet 

If the API key is for the Bybit testnet, set SANDBOX to True. If using the Live
exchange, set SANDBOX to False.
```python
SANDBOX = True
```

### Set Symbol 

Go to https://www.bybit.com/data/markets/ for full list of available market 
symbols.

If the Trader only wants to trade one market, they should enter the SYMBOL as a 
string in quotes. 
```python 
SYMBOL = 'BTC/USD'
```

If trading multiple SYMBOLs is desired, provide a list of strings.
```python 
SYMBOL = ['BTC/USD','ETH/USD']
```

If the Trader's funds are in USDT, and they want to scan every cryptocurrency 
that pairs with USDT, just provide 'USDT' as a string.
```python 
SYMBOL = 'USDT'
```

### Set Timeframe 

Bybit makes OHLCV data of multiple timeframes available for setting TIME_FRAME 
with. A list of these and the string by which to reference them can be found 
below.
| Time Frame | Reference String |
| ---------- | ---------------- |
| 1 Minute   | '1m'             |
| 3 Minute   | '3m'             |
| 5 Minute   | '5m'             |
| 15 Minute  | '15m'            |
| 30 Minute  | '30m'            |
| 45 Minute  | '45m'            |
| 1 Hour     | '1h'             |
| 2 Hour     | '2h'             |
| 4 Hour     | '4h'             |
| 6 Hour     | '6h'             |
| 12 Hour    | '12h'            |
| 1 Day      | '1d'             |
| 1 Week     | '1w'             |
| 1 Month    | '1M'             |

Below is an example of setting TIME_FRAME to 1 hour in config.py.
```python 
TIME_FRAME = '1h'
```

### Set Position Amount 

If it is desired to enter into every position with a specific dollar amount, then
assign that value as an integer.
```python 
AMOUNT = 100
```

If it is desired to use a percentage of the available account, then assign the 
percentage as a string value in quotes.
```python 
AMOUNT = '30'
```

### Leverage 

Set LEVERAGE with an integer. For 5x leverage, set LEVERAGE to 5.
```python 
LEVERAGE = 5
```

### Stoploss 

STOPLOSS is set with percent as a decimal. If the Trader wants to restrict the 
risk on the position to 15 percent, they would assign .15, i.e., 15/100.
```python 
STOPLOSS = .15
```

### Take Profit 

TAKEPROFIT is set with percent as a decimal. If the Trader wants to take profit 
on the position when it reaches 35 percent, they would assign .35, i.e., 35/100.
```python 
TAKEPROFIT = .35
```


[^1]: At this time, there is only one strategy to choose from, but in the future I would
    like to add more options or make the code more modular so a trader can code a 
    custom strategy as a class and drop it in the project directory.

[^2]: Supertrend is a trend detecting indicator that uses two parameters, 
    look-back period and multiplier. It consists of an upperband and lowerband.
    The upperband is calculated with the following:
    
    BASIC_UPPER_BAND = (HIGH + LOW)/2 + (MULTIPLIER * AVERAGE_TRUE_RANGE)
    BASIC_LOWER_BAND = (HIGH + LOW)/2 - (MULTIPLIER * AVERAGE_TRUE_RANGE)
    
    And AVERAGE_TRUE_RANGE is determined using the parameter passed in as the
    look-back period.