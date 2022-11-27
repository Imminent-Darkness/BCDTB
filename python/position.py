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

class Position:
    def getPosition(self, exchange, symbol, attempt=0):
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
            market = exchange.market(symbol)
            
            # Determines which market based off how ticker string ends
            if symbol.endswith('USD'):
                response = self.exchange.v2_private_get_position_list({'symbol':market['id']})
            elif symbol.endswith('USDT'):
                response = exchange.private_linear_get_position_list({'symbol':market['id']})
            else:
                response = exchange.futures_private_position_list({'symbol':market['id']})
            position = response['result']
            
            if position['size'] == '0':
                position = 'None'
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(exchange.id, 
                  'futures_private_position_list failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.getPosition(attempt)
        except ccxt.ExchangeError as e:
            print(self.exchange.id, 
                  'futures_private_position_list failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.getPosition(attempt)
        except Exception as e:
            print(self.exchange.id, 
                  'futures_private_position_list failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.getPosition(attempt)
        
        return position


    def inPosition(self, exchange, symbol):
        return (self.getPosition(exchange, symbol) != 'None')


    def long(self, exchange, symbol, amount, leverage, take_profit, safety_margin, attempt=0):
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to open long position.')
            raise SystemExit
        
        try:
            last_ticker = exchange.fetch_ticker(symbol)
            last_price = last_ticker['last']

            type = 'market'
            side = 'Buy'
            amount = float(int(amount))
            price = None
            order = exchange.create_order(  symbol, 
                                            type, 
                                            side, 
                                            amount, 
                                            price, 
                                            {   'qty': amount, 
                                                'basePrice': last_price, 
                                                'take_profit': take_profit, 
                                                'stop_loss': safety_margin
                                            })
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(exchange.id, 
                  'create_order (long) failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.long(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin, 
                        attempt
                        )
        except ccxt.ExchangeError as e:
            print(exchange.id, 
                  'create_order (long) failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.long(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        except Exception as e:
            print(exchange.id, 
                  'create_order (long) failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.long(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        
        return order


    def short(self, exchange, symbol, amount, leverage, take_profit, safety_margin, attempt=0):
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to open short position.')
            raise SystemExit
        
        try:
            last_ticker = exchange.fetch_ticker(symbol)
            last_price = last_ticker['last']

            type = 'market'
            side = 'Sell'
            amount = float(int(amount))
            price = None
            order = exchange.create_order(  symbol, 
                                            type, 
                                            side, 
                                            amount, 
                                            price, 
                                            {   'qty': amount, 
                                                'basePrice': last_price, 
                                                'take_profit': take_profit, 
                                                'stop_loss': safety_margin
                                            })
        
        # Exception handling as suggested in the ccxt documentation
        # https://docs.ccxt.com/en/latest/manual.html#error-handling
        except ccxt.NetworkError as e:
            print(exchange.id, 
                  'create_order (short) failed due to a network error:', 
                  str(e)
                  )
            time.sleep(5)
            self.short(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin, 
                        attempt
                        )
        except ccxt.ExchangeError as e:
            print(exchange.id, 
                  'create_order (short) failed due to exchange error:', 
                  str(e)
                  )
            time.sleep(5)
            self.short(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        except Exception as e:
            print(exchange.id, 
                  'create_order (short) failed with:', 
                  str(e)
                  )
            time.sleep(5)
            self.short(  exchange,
                        symbol, 
                        amount, 
                        leverage, 
                        take_profit, 
                        safety_margin,
                        attempt
                        )
        
        return order


    def close(self, exchange, symbol):
        # Exits function after 5 connection attempts 
        # to avoid infinite loop
        attempt = attempt + 1
        if attempt > 5:
            print('Unable to close position.')
            raise SystemExit
        
        # First get open position
        position = self.getPosition(exchange, symbol)
        type = 'Market'
        side = 'Buy' if position['side'] == 'Sell' else 'Sell'
        amount = float(int(position['size']))
        price = None
        
        # If position is found, close it
        if position != 'None':
            try:
                closed_order = exchange.create_order(   symbol, 
                                                        type, 
                                                        side, 
                                                        amount, 
                                                        price, 
                                                        {   'time_in_force': 'ImmediateOrCancel', 
                                                            'reduce_only': True, 
                                                            'close_on_trigger': True
                                                        })
            
            # Exception handling as suggested in the ccxt documentation
            # https://docs.ccxt.com/en/latest/manual.html#error-handling
            except ccxt.NetworkError as e:
                print(exchange.id, 
                      'create_order (cancel) failed due to a network error:', 
                      str(e)
                      )
                time.sleep(5)
                self.close(exchange, symbol, attempt)
            except ccxt.ExchangeError as e:
                print(exchange.id, 
                      'create_order (cancel) failed due to exchange error:', 
                      str(e)
                      )
                time.sleep(5)
                self.close(exchange, symbol, attempt)
            except Exception as e:
                print(exchange.id, 
                      'create_order (cancel) failed with:', 
                      str(e)
                      )
                time.sleep(5)
                self.close(exchange, symbol, attempt)
        return closed_order
