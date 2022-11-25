#       Steven Wilkins
#       CS401-Capstone Project

#       Python class description:   
#           myasset.py creates a dedicated object for each traded
#           currency pair. This object provides the means for the
#           main program to fetch price data associated with the
#           pair from the exchange, use a technical analysis 
#           strategy to detect buy and sell signals, enter long
#           and short leveraged positions trading that pair, and
#           properly close those positions.

import ccxt
import pandas as pd
import mplfinance as mpf
import warnings
import numpy as np
import time
from datetime import datetime
from pprint import pprint
import os
import glob

pd.set_option('display.max_rows', None)
warnings.filterwarnings('ignore')


class Myasset:
    def __init__(self, exchange, symbol, timeframe, amount, leverage, stoploss, takeprofit):
        self.exchange = exchange
        self.symbol = symbol
        self.df = pd.DataFrame()
        self.amount = amount
        self.trade_amount = amount
        self.leverage = leverage
        self.timeframe = timeframe
        self.stoploss = stoploss
        self.takeprofit = takeprofit

    
    def __repr__(self):
        Myasset_string =    f" \
            ********************************* \n \
                    Asset Information         \n \
                                              \n \
              Exchange: {self.exchange}       \n \
              Symbol: {self.symbol}           \n \
              Amount: {self.amount}           \n \
              Leverage: {self.leverage}       \n \
              Timeframe: {self.timeframe}     \n \
              Stoploss: {self.stoploss}       \n \
              Takeprofit: {self.takeprofit}   \n \
            ********************************* \n\n"
        return Myasset_string
    

    def get_df(self):
        
        return self.df
    

    def __get_last_ticker(self, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to fetch last ticker')
            raise SystemExit
        
        # Tries to connect to exchange to fetch last ticker
        try:
            last_ticker = self.exchange.fetch_ticker(self.symbol)
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'fetch_ticker failed due to a network error:', 
                  str(e)
                  )
            self.__get_last_ticker(attempt)        
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'fetch_ticker failed due to exchange error:', 
                  str(e)
                  )
            self.__get_last_ticker(attempt)        
        except Exception as e:
            print(self.exchange.id, 
                  'fetch_ticker failed with:', 
                  str(e))
            self.__get_last_ticker(attempt)
        
        return last_ticker
    

    def __get_wallet_balance(self, last_px, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to connect fetch wallet balance.')
            raise SystemExit

        # Determine wallet being used
        if self.symbol.endswith('USD'):
            wallet = self.symbol.replace("/USD","")
        elif self.symbol.endswith('USDT'):
            wallet = 'USDT'
        else:
            print('failed to determine wallet being used...')
            
        # Attempt to fetch wallet balances for base currency
        try:
            print()
            print(f"fetching {wallet} balance...")
            balance = self.exchange.fetch_balance()
            
            # show balance in cryptocurrency
            print(f"Total balance [{self.symbol}]: {balance[wallet]['total']}")
            print(f"Available balance [{self.symbol}]: {balance[wallet]['free']}")
            
            # convert balance to USD
            total = last_px * balance[wallet]['total']
            available = last_px * balance[wallet]['free']
            
            # show balance in USD
            print(f"Total balance [dollars]: ${total}")
            print(f"Available balance [dollars]: ${available}")
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'fetch_balance failed due to a network error:', 
                  str(e)
                  )
            self.__get_wallet_balance(last_px, attempt)
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'fetch_balance failed due to exchange error:', 
                  str(e)
                  )
            self.__get_wallet_balance(last_px, attempt)
        except Exception as e:
            print(self.exchange.id, 
                  'fetch_balance failed with:', 
                  str(e)
                  )
            self.__get_wallet_balance(last_px, attempt)
        
        return total, available
    

    def __set_trade_amount(self, available, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to set trade amount.')
            raise SystemExit
        
        # If amount is set with a string in config.py, it is interpreted as
        # percent of available account balance.
        if type(self.amount) == str:
            
            # calculate position size based on percent supplied by user
            try:
                
                # Replace (.) in case user passed percentage as decimal
                amnt = self.amount.replace(".","")
                
                # Convert percent value to integer and divide by 100
                percent = (int(amnt))/100
                
                # Multiply percent by available balance
                self.trade_amount = percent * available
                print(f"Trade amount for {self.symbol} is {self.trade_amount}")
            
            # Handle exceptions and retry
            except Exception as e:
                print('set_trade_amount failed with error:', str(e))
                self.__set_trade_amount(available, attempt)

    
    def __create_ohlcv_df(self, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to create ohlcv df.')
            raise SystemExit
        
        # Attempt to fetch ohlcv data and store it in a pandas dataframe
        try:
            print()
            print(f"Fetching {self.symbol} time frame bars for {datetime.now().isoformat()}...")
            bars = self.exchange.fetch_ohlcv(self.symbol, 
                                             self.timeframe, 
                                             limit=200
                                             )
            df = pd.DataFrame(bars[:-1], 
                              columns=['Timestamp', 
                                       'Open', 
                                       'High', 
                                       'Low', 
                                       'Close', 
                                       'Volume'
                                       ]
                              )
            # Converts timestamp of each entry from string to datetime object
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'fetch_ohlcv failed due to a network error:', 
                  str(e)
                  )
            self.__create_ohlcv_df(attempt)
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'fetch_ohlcv failed due to exchange error:', 
                  str(e)
                  )
            self.__create_ohlcv_df(attempt)
        except Exception as e:
            print(self.exchange.id, 
                  'fetch_ohlcv failed with:', 
                  str(e)
                  )
            self.__create_ohlcv_df(attempt)
        
        return df


    def __plot_chart(self, df, style='yahoo'):
        
        # Constrains cart window to last 50 candles
        df_window = df[-50:]
        
        # Assembles additional indicators into a variable to pass to mplfinance
        apds =  [    mpf.make_addplot(df_window['print_lb1'],color='green',panel=0),
                     mpf.make_addplot(df_window['print_ub1'],color='red',panel=0),
                     mpf.make_addplot(df_window['print_lb2'],color='green',panel=0),
                     mpf.make_addplot(df_window['print_ub2'],color='red',panel=0),
                     mpf.make_addplot(df_window['print_lb3'],color='green',panel=0),
                     mpf.make_addplot(df_window['print_ub3'],color='red',panel=0),
                     mpf.make_addplot(df_window['50_ewm'],color='orange',panel=0),
                     mpf.make_addplot(df_window['200_ewm'],color='purple',panel=0),
                     mpf.make_addplot(df_window['Signal_L'],color='blue',type='scatter',marker='^',markersize=100,panel=0),
                     mpf.make_addplot(df_window['Signal_S'],color='orange',type='scatter',marker='v',markersize=100,panel=0),
                     mpf.make_addplot(df_window['Stoch_K'], color='blue', ylim=[0, 100], panel=1, ylabel='Stoch'),
                     mpf.make_addplot(df_window['Stoch_D'], color='orange', panel=1),
                     mpf.make_addplot(df_window['Stoch_SD'], color='red', panel=1),
                     mpf.make_addplot(df_window['Stoch_UL'], color='grey', panel=1, linestyle='--'),
                     mpf.make_addplot(df_window['Stoch_DL'], color='grey', panel=1, linestyle='--')
        ]
        
        # Create directory to store generated charts
        
        # Removes (/) from symbol so it can be used in naming the charts
        name = self.symbol.replace("/", "")
        
        # Gets current working directory
        parent_dir = os.getcwd()
        
        # Creates /data/charts/{symbol}-charts/ path inside 
        # program directory to store generated charts
        directory = "data"
        path = os.path.join(parent_dir, directory)
        directory = "charts"
        path = os.path.join(parent_dir, directory)
        directory = f"{name}-charts"
        path = os.path.join(path, directory)
        
        # Makes directory with created path
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory {path} created successfully")
        except OSError as error:
            print(f"os.makedirs() failed with {error}")

        # Count files in directory
        num = len(glob.glob(path + f"/{name}-chart*.png"))
        
        # Names each new chart as {symbol}-chart(x).png where x is an ascending number
        filepath = f"{path}/{name}-chart({num}).png"
        
        # Creates chart with indicators
        chart = mpf.plot(df_window, 
                         addplot=apds, 
                         type='candle',
                         style='yahoo', 
                         savefig=filepath, 
                         returnfig=True, 
                         block=False
                         )
        
        return chart #, panel_ratios=(5, 1), tight_layout=True


    def __tr(self, df):
        
        # Preparing pandas dataframe for calculating true range
        df['previous_close'] = df['Close'].shift(1)
        df['high-low'] = abs(df['High'] - df['Low'])
        df['high-pc'] = abs(df['High'] - df['previous_close'])
        df['low-pc'] = abs(df['Low'] - df['previous_close'])

        # Calculate true range for the whole pandas dataframe
        tr = df[['high-low', 'high-pc', 'low-pc']].max(axis=1)

        return tr


    def __atr(self, df, period):
        
        # Calculate average true range for the whole pandas dataframe
        df['tr'] = self.__tr(df)
        atr = df['tr'].rolling(period).mean()

        return atr
    

    def __supertrend(self, df, period, atr_multiplier, label):

        # Prepare pandas dataframe for storing supertrend data
        # The (label) variable allows the dataframe to store multiple supertrend instances
        hl2 = (df['High'] + df['Low']) / 2
        df[f'atr{label}'] = self.__atr(df, period)
        df[f'upperband{label}'] = hl2 + (atr_multiplier * df[f'atr{label}'])
        df[f'lowerband{label}'] = hl2 - (atr_multiplier * df[f'atr{label}'])
        df[f'in_uptrend{label}'] = True
        df[f'print_ub{label}'] = df[f'upperband{label}']
        df[f'print_lb{label}'] = df[f'lowerband{label}']

        # Iterate through whole dataframe and set supertrend values
        for current in range(1, len(df.index)):
            previous = current - 1

            # Checks if in uptrend and prints green lowerband
            if df['Close'][current] > df[f'upperband{label}'][previous]:
                df[f'in_uptrend{label}'][current] = True
                df[f'print_lb{label}'][current] = df[f'lowerband{label}'][current]
            
            # Checks if in downtrend and prints red upperband
            elif df['Close'][current] < df[f'lowerband{label}'][previous]:
                df[f'in_uptrend{label}'][current] = False
                df[f'print_ub{label}'][current] = df[f'upperband{label}'][current]
            
            # Prepares for sign of trend reversal by horizontally flattening the 
            # printed band by assigning the previous value in the current position 
            else:
                
                # Trend direction stays the same
                df[f'in_uptrend{label}'][current] = df[f'in_uptrend{label}'][previous]

                # If in uptrend and current lowerband value is lower than previous one, the
                # current value will be replaced with the previous one to flatten the band
                if (df[f'in_uptrend{label}'][current] and 
                    df[f'lowerband{label}'][current] < df[f'lowerband{label}'][previous]):
                    
                    df[f'lowerband{label}'][current] = df[f'lowerband{label}'][previous]

                # If in downtrend and current upperband value is higher than previous one, the
                # current value will be replaced with the previous one to flatten the band
                if not (df[f'in_uptrend{label}'][current] and 
                        df[f'upperband{label}'][current] > df[f'upperband{label}'][previous]):
                    
                    df[f'upperband{label}'][current] = df[f'upperband{label}'][previous]

            # When in uptrend, only green lowerband is shown.
            # When in downtrend, only red upperband is shown.
            if df[f'in_uptrend{label}'][current] == True:
                df[f'print_ub{label}'][current] = np.nan
            else:
                df[f'print_lb{label}'][current] = np.nan

        return df


    def __entry_signals(self, df, macro):

        ul = 80
        dl = 20
        df['Signal_L'] = df['Low']
        df['Signal_S'] = df['High']
        df['Signal_L'][0] = np.nan
        df['Signal_S'][0] = np.nan

        for current in range(1, (len(df.index)-1)):
            previous = current - 1
            up = False
            down = False
            currK = df['Stoch_K'][current]
            currD = df['Stoch_D'][current]
            currSD = df['Stoch_SD'][current]
            prevK = df['Stoch_K'][previous]
            prevD = df['Stoch_D'][previous]
            #prevSD = df['Stoch_SD'][previous]

            if not df['in_uptrend2'][previous] and df['in_uptrend2'][current]:

                if macro:
                    if currSD <= dl:
                        if (currK > currD) and (prevK <= prevD):
                            up = True
   #                     else:
   #                         pass
   #                 else:
   #                     pass
   #             else:
   #                 pass

            elif df['in_uptrend2'][previous] and not df['in_uptrend2'][current]:

                if not macro:
                    if currSD >= ul:
                        if (currK < currD) and (prevK >= prevD):
                            down = True
   #                     else:
   #                         pass
   #                 else:
   #                     pass
   #             else:
   #                 pass
            
            if up:
                df['Signal_S'][current] = np.nan
            elif down:
                df['Signal_L'][current] = np.nan
            else:
                df['Signal_L'][current] = np.nan
                df['Signal_S'][current] = np.nan
            
        return df


    def __computeRSI (self, data, time_window):
        diff = data.diff(1).dropna()        # diff in one field(one day)

        #this preservers dimensions off diff values
        up_chg = 0 * diff
        down_chg = 0 * diff
        
        # up change is equal to the positive difference, otherwise equal to zero
        up_chg[diff > 0] = diff[ diff>0 ]
        
        # down change is equal to negative deifference, otherwise equal to zero
        down_chg[diff < 0] = diff[ diff < 0 ]
        
        # check pandas documentation for ewm
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
        # values are related to exponential decay
        # we set com=time_window-1 so we get decay alpha=1/time_window
        up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
        
        rs = abs(up_chg_avg/down_chg_avg)
        rsi = 100 - 100/(1+rs)
        return rsi


    def __stochastic(self, data, k_window, d_window, window):

        
        min_val  = data.rolling(window=window, center=False).min()
        max_val = data.rolling(window=window, center=False).max()
        
        stoch = ( (data - min_val) / (max_val - min_val) ) * 100
        
        k = stoch.rolling(window=k_window, center=False).mean() 
        d = k.rolling(window=d_window, center=False).mean()
        sd = d.rolling(window=d_window, center=False).mean()
        ul = 80
        dl = 20
        
        return k, d, sd, ul, dl
    

    def __get_position(self, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to set trade amount.')
            raise SystemExit
        
        # Attempts to fetch current position
        try:
            position = 'None'
            #print(f"******* FETCHING {self.symbol} POSITION *******")
            market = self.exchange.market(self.symbol)
            
            # Determines which market based off how ticker string ends
            if self.symbol.endswith('USD'):
                response = self.exchange.v2_private_get_position_list({'symbol':market['id']})
            elif self.symbol.endswith('USDT'):
                response = self.exchange.private_linear_get_position_list({'symbol':market['id']})
            else:
                response = self.exchange.futures_private_position_list({'symbol':market['id']})
            position = response['result']
            
            if position['size'] == '0':
                position = 'None'
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'futures_private_position_list failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__get_position(attempt)
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'futures_private_position_list failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__get_position(attempt)
        except Exception as e:
            print(self.exchange.id, 
                  'futures_private_position_list failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.get_position(attempt)
        
        return position
    
    
    def in_position(self):
        
        return (self.__get_position() != 'None')


    def __close_position(self, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to close position.')
            raise SystemExit
        
        # First get open position
        position = self.__get_position()
        type = 'Market'
        side = 'Buy' if position['side'] == 'Sell' else 'Sell'
        amount = float(int(position['size']))
        price = None
        
        # If position is found, close it
        if position != 'None':
            try:
                closed_order = self.exchange.create_order(self.symbol, 
                                                          type, 
                                                          side, 
                                                          amount, 
                                                          price, {'time_in_force': 'ImmediateOrCancel', 
                                                                  'reduce_only': True, 
                                                                  'close_on_trigger': True
                                                                  })
            
            # Exception handling as suggested in the ccxt documentation
            # https://docs.ccxt.com/en/latest/manual.html#error-handling
            except ccxt.NetworkError as e:
                print(self.exchange.id, 
                      'create_order (cancel) failed due to a network error:', 
                      str(e)
                      )
                time.sleep(5)
                self.__close_position(attempt)
            except ccxt.ExchangeError as e:
                print(self.exchange.id, 
                      'create_order (cancel) failed due to exchange error:', 
                      str(e)
                      )
                time.sleep(5)
                self.__close_position(attempt)
            except Exception as e:
                print(self.exchange.id, 
                      'create_order (cancel) failed with:', 
                      str(e)
                      )
                time.sleep(5)
                self.__close_position(attempt)
        return closed_order


    def __long(self, symbol: str, amount: float, leverage: int, take_profit, safety_margin, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to open long position.')
            raise SystemExit
        
        try:
            last_ticker = self.exchange.fetch_ticker(symbol)
            last_price = last_ticker['last']

            type = 'market'
            side = 'Buy'
            amount = float(int(amount))
            price = None
            order = self.exchange.create_order(symbol, 
                                               type, 
                                               side, 
                                               amount, 
                                               price, {'qty': amount, 
                                                       'basePrice': last_price, 
                                                       'take_profit': take_profit, 
                                                       'stop_loss': safety_margin
                                                       })
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'create_order (long) failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__long(symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin, 
                        attempt
                        )
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'create_order (long) failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__long(symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        except Exception as e:
            print(self.exchange.id, 
                  'create_order (long) failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.__long(symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        
        return order


    def __short(self, symbol: str, amount: float, leverage: int, take_profit, safety_margin, attempt=0):
        
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to open short position.')
            raise SystemExit
        
        try:
            last_ticker = self.exchange.fetch_ticker(symbol)
            last_price = last_ticker['last']

            type = 'market'
            side = 'Sell'
            amount = float(int(amount))
            price = None
            order = self.exchange.create_order(symbol, 
                                               type, 
                                               side, 
                                               amount, 
                                               price, {'qty': amount, 
                                                       'basePrice': last_price, 
                                                       'take_profit': take_profit, 
                                                       'stop_loss': safety_margin
                                                       })
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(self.exchange.id, 
                  'create_order (short) failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__short(symbol, 
                         amount, 
                         leverage, 
                         take_profit, 
                         safety_margin, 
                         attempt
                         )
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'create_order (short) failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.__short(symbol, 
                         amount, 
                         leverage, 
                         take_profit, 
                         safety_margin,
                         attempt
                         )
        except Exception as e:
            print(self.exchange.id, 
                  'create_order (short) failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.__short(symbol, 
                         amount, 
                         leverage, 
                         take_profit, 
                         safety_margin,
                         attempt
                         )
        
        return order


    def __check_buy_sell_signals(self, df: object, macro: bool, price: float):

        print("checking for buy and sell signals...")

        last_row = len(df.index) - 1
        previous_row = last_row - 1
        
        # Check for stochastic entries
        currentD = df['Stoch_D'][last_row]
        previousD = df['Stoch_D'][previous_row]
        currentSD = df['Stoch_SD'][last_row]
        currentK = df['Stoch_K'][last_row]
        previousK = df['Stoch_K'][previous_row]

        if df['in_uptrend3'][last_row]:
            
            print('Checking if in micro uptrend...')
            
            if not (df['in_uptrend2'][previous_row] 
                    and df['in_uptrend2'][last_row]):
                
                print("changed to uptrend, buy if price is above wma")

                if macro:
                    
                    if currentSD <= 20:
                        
                        if ((currentK > currentD) 
                            and (previousK <= previousD)):
                            
                            if not self.in_position():
                                
                                print("creating long position...")
                                last_ticker = self.__get_last_ticker()
                                last_px = last_ticker['last']
                                total, available = self.__get_wallet_balance(last_px)
                                self.__set_trade_amount(available)
                                #self.df = self.__create_ohlcv_df()
                                pprint(self.__long(self.symbol, 
                                                   self.trade_amount, 
                                                   self.leverage, 
                                                   take_profit=(price+(
                                                       (price*self.takeprofit)/self.leverage
                                                       )), 
                                                   safety_margin=(price-(
                                                       (price*self.stoploss)/self.leverage
                                                       )))
                                       )
                            else:
                                print("Already in long position...")
                else:
                    print("either the price is not above the weighted moving average")
                    print(" or we are already in position")

        
        
        if df['in_uptrend3'][last_row]:
            
            if (df['in_uptrend2'][previous_row] 
                and not df['in_uptrend2'][last_row]):
                
                print("changed to downtrend, sell")

                if not macro:
                    
                    if currentSD >= 80:
                        
                        if ((currentK < currentD) 
                            and (previousK >= previousD)):
                            
                            if not self.in_position():
                                
                                print("creating short position")
                                last_ticker = self.__get_last_ticker()
                                last_px = last_ticker['last']
                                total, available = self.__get_wallet_balance(last_px)
                                self.__set_trade_amount(available)
                                pprint(self.__short(self.symbol, 
                                                    self.trade_amount, 
                                                    self.leverage, 
                                                    take_profit=(price-(
                                                        (price*self.takeprofit)/self.leverage
                                                        )), 
                                                    safety_margin=(price+(
                                                        (price*self.stoploss)/self.leverage
                                                        )))
                                       )
                            else:
                                print("Already in short position...")
                else:
                    print("either the price is not below the weighted moving average")
                    print("or we are already in position")
            

    def __check_candles(df: object, macro: bool):
        if macro:
            df.ta.cdl_pattern(name=["morningdojistar","morningstar","inside","engulfing"],append=True)            
            

    def run_bot(self):
            
        last_ticker = self.__get_last_ticker()
        last_px = last_ticker['last']
        #total, available = self.__get_wallet_balance(last_px)

        #self.__set_trade_amount(available)
        self.df = self.__create_ohlcv_df()
        
        
        # Calculate 50 period ewm
        self.df['50_ewm'] = self.df['Close'].ewm(span=50,
                                                 min_periods=0,
                                                 adjust=False,
                                                 ignore_na=False
                                                 ).mean()
        # Calculate 200 period ewm
        self.df['200_ewm'] = self.df['Close'].ewm(span=200,
                                                  min_periods=0,
                                                  adjust=False,
                                                  ignore_na=False
                                                  ).mean()
    
        # Calculate moving average
        #df['50_ma'] = df['Close'].rolling(window=50,min_periods=0).mean()
        #df['200_ma'] = df['Close'].rolling(window=200,min_periods=0).mean()    
    
        # Calculate macro trend using 200 wma
        #macroUP = last_px > last_wma
        
        # Calculate macro trend using cross of 14 and 42 ewm
        lastRow = len(self.df.index) -1
        macroUP = self.df['50_ewm'][lastRow] > self.df['200_ewm'][lastRow]
    
        self.df.set_index("Timestamp", inplace=True)    
    
        self.df['RSI'] = self.__computeRSI(self.df['Close'], 14)
        self.df[['Stoch_K',
                 'Stoch_D',
                 'Stoch_SD',
                 'Stoch_UL',
                 'Stoch_DL']] = self.__stochastic(self.df['RSI'], 3, 3, 14)
        
    
        self.df = self.__supertrend(self.df, 
                                    period=12, 
                                    atr_multiplier=3, 
                                    label='1'
                                    )
        self.df = self.__supertrend(self.df, 
                                    period=11, 
                                    atr_multiplier=2, 
                                    label='2'
                                    )
        self.df = self.__supertrend(self.df, 
                                    period=10, 
                                    atr_multiplier=1, 
                                    label='3'
                                    )
        self.df = self.__entry_signals(self.df, macroUP)
        
        self.__check_buy_sell_signals(self.df, macroUP, last_px)
        
    
        try:
            self.__plot_chart(self.df)
        except:
            pass
        
        print('done')
        '''
        stop = time.perf_counter()
        runtime = stop - start
        print(f"object process runtime is {runtime}...")
        '''
        '''
        print()
        print()
        print()
        print()
        price = last_px
        take_profit=(price+((price*self.takeprofit)/self.leverage))
        safety_margin=(price-((price*self.stoploss)/self.leverage))
        print(f"price: {price}")
        print(f"take_profit: {take_profit}")
        print(f"safety_margin: {safety_margin}")
        order = self.__long(self.symbol, self.trade_amount, self.leverage, take_profit, safety_margin)
        pprint(order)
        print()
        print("in_position() check:")
        print(self.in_position())
        print()
        print()
        print("SHOULD PRINT AN OPEN POSITION BELOW")
        pprint(self.__get_position())
        print()
        print()
        closed_position = self.__close_position()
        pprint(closed_position)
        print()
        print()
        print("in_position() check:")
        print(self.in_position())
        print()
        print("SHOULD PRINT NO POSITION BELOW")
        pprint(self.__get_position())
        print()
        print()
        '''
        
