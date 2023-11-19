    from freqtrade.strategy import IStrategy
    from typing import Dict, List
    from functools import reduce
    from pandas import DataFrame
    # --------------------------------

    import talib.abstract as ta
    import freqtrade.vendor.qtpylib.indicators as qtpylib


    class alperemasrsi(IStrategy):
        """
        Alper srsi + ema25 20231119
        """

        INTERFACE_VERSION: int = 3
        minimal_roi = {
            "60":  0.01,
            "30":  0.03,
            "20":  0.04,
            "0":  0.05
        }

        stoploss = -0.10
        timeframe = '15m'
        trailing_stop = False
        trailing_stop_positive = 0.01
        trailing_stop_positive_offset = 0.02
        process_only_new_candles = True
        use_exit_signal = True
        exit_profit_only = True
        ignore_roi_if_entry_signal = False

        order_types = {
            'entry': 'limit',
            'exit': 'limit',
            'stoploss': 'market',   
            'stoploss_on_exchange': False
        }

        # Hyperopta uygun rsi değerleri
        rsi_oversold_buy = DecimalParameter(10, 80, decimals=5, default=20, space="buy")
        rsi_oversold_sell = DecimalParameter(10, 80, decimals=5, default=80, space="sell")

        def informative_pairs(self):
            """
            Define additional, informative pair/interval combinations to be cached from the exchange.
            These pair/interval combinations are non-tradeable, unless they are part
            of the whitelist as well.
            For more information, please consult the documentation
            :return: List of tuples in the format (pair, interval)
                Sample: return [("ETH/USDT", "5m"),
                                ("BTC/USDT", "15m"),
                                ]
            """
            return []

        def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

            dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
            dataframe['ema25'] = ta.EMA(dataframe, timeperiod=25)
            dataframe['ema30'] = ta.EMA(dataframe, timeperiod=30)
            dataframe['ema35'] = ta.EMA(dataframe, timeperiod=35)
            dataframe['ema40'] = ta.EMA(dataframe, timeperiod=40)
            dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
            dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
            dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
            dataframe['stoch_rsi'] = ta.momentum.stochrsi(close=dataframe['close'], window=14, smooth1=3, smooth2=3)

            return dataframe

        def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
            dataframe.loc[

               
               (
               
                    (
                                (dataframe['ema100'] > dataframe['ema200']) &
                                (dataframe['ema50'] < dataframe['ema40']) &
                                (dataframe['ema40'] < dataframe['ema35']) &
                                (dataframe['ema35'] < dataframe['ema30']) &
                                (dataframe['ema30'] < dataframe['ema20']) &
                                (dataframe['volume'] > 0)
                    ) &
                
                    (dataframe['stoch_rsi'] < self.rsi_oversold_buy.value) & #rsi rsi_oversold_buy değerinden küçükse
                    #(dataframe['open'] > dataframe['close']) & # mum kırmızı ise
                    (dataframe['close'] > dataframe['ema25'])  # mum ema 25 üzerinde ise
                ),
                'enter_long'] = 1

            return dataframe

         def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
             dataframe.loc[
                 (
                     (dataframe['close'] < dataframe['ema25'])  
                 ),
                 'exit_long'] = 1
         
             return dataframe
