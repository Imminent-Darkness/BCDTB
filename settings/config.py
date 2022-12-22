# config.py

API_KEY = 'YourAPIkey'
SECRET_KEY = 'YourSecretKey'

# Are you using a testnet key: True or False

SANDBOX = True      

# Individually: 'BTC/USD', 'ETH/USD', 'BTC/USDT', 'ETH/USDT'...
# List: ['BTC/USD','ETH/USD','LINK/USDT',...]
# Scan all USDT pairs: 'USDT'

SYMBOL = 'BTC/USD'

# 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w, 1M

TIME_FRAME = '1m'   

# Enter total desired position size after applying leverage. 
# Amount can be a specific dollar amount or a calculated percentage 
# of the Trader's account at the time of entering the position. 
# To use set amount, provide the number with no quotes around it and include
# a decimal in the number whether it needs it or not. 
# Example for $100 position every trade   --------->  AMOUNT = 100.0
# Example for 80% of wallet balance each trade  --->  AMOUNT = "80"

AMOUNT = "80"      

# Enter leverage up to 100 for BTC and ETH, 
# other coins only allow leverage up to either 25 or 50

LEVERAGE = 5

# Formula for STOP_LOSS --> (x/100) --> where x=percent. 
# This will keep you from losing your whole account if things 
# go wrong. Calculation for 15% --> (15 / 100) = .15 

STOP_LOSS = .15     

# Formula for TAKE_PROFIT --> (x/100) --> where x=percent.
# Decide what percent profit you would like to reach before 
# exiting a position and divide that number by 100.
# Calculation for 35% --> (35/100) = .35

TAKE_PROFIT = .35

# Set to True if you want the software to use buy and sell signals to 
# exit positions.

SIGNAL_EXIT = False
