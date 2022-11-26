# strategy

class Strategy:
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
        