# https://github.com/CanerIrfanoglu/medium

import talib
from talib import abstract
import pandas as pd
import numpy as np
from datetime import date


class TechnicalAnalysis:

    @staticmethod
    def _getSupport(df: pd.DataFrame, i: int):
        supportPrice = 0
        if df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]:
            supportPrice = df['low'][i]
        return supportPrice

    @staticmethod
    def _getResistance(df: pd.DataFrame, i: int):
        resistancePrice = 0
        if df['high'][i] > df['high'][i-1] and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]:
            resistancePrice = df['high'][i]
        return resistancePrice

    @staticmethod
    def KeyLevels(df: pd.DataFrame):
        allPrices = []
        for i in range(2, df.shape[0] - 2):
            supportPrice = TechnicalAnalysis._getSupport(df, i)
            resistantPrice = TechnicalAnalysis._getResistance(df, i)
            if supportPrice != 0:
                allPrices.append((i, supportPrice))
            elif resistantPrice != 0:
                allPrices.append((i, resistantPrice))

        # df['Date'] = pd.to_datetime(df.index)
        # df['Date'] = df['Date'].apply(mpl_dates.date2num)
        # df = df.loc[:, ['Date', 'open', 'high', 'low', 'close']]

        # get rid of prices near to one another reduce noise

        mean = np.mean(df['high'] - df['low'])  # rough estimate of volatility

        allPrices = []

        for i in range(2, df.shape[0] - 2):
            supportPrice = TechnicalAnalysis._getSupport(df, i)
            resistantPrice = TechnicalAnalysis._getResistance(df, i)
            if supportPrice != 0:
                if np.sum([abs(supportPrice-x) < mean for x in allPrices]) == 0:
                    allPrices.append((i, supportPrice))
            elif resistantPrice != 0:
                if np.sum([abs(resistantPrice-x) < mean for x in allPrices]) == 0:
                    allPrices.append((i, resistantPrice))
        sr_lines = []
        for item in allPrices:
            tstamp = df.iloc[item[0]].name
            stamp = str(tstamp)
            sr_lines.append((item[0], stamp, item[1]))
        return sr_lines

    # convert timestamp to datetime string

    @staticmethod
    def OvernightGappers(df: pd.DataFrame, params: dict = None):
        minPrice = 0.20
        percentGapper = 0.05
        if 'minprice' in params:
            minPrice = params['minprice']   # minimum price gap
        if 'percentgapper' in params:
            percentGapper = params['percentgapper']
        on_gappers = []
        for i in range(0, df.shape[0]-2):
            overnightGapper = 0
            gap = df.iloc[i].close - df.iloc[i+1].open
            calcPercent = abs(gap / df.iloc[i].close)
            if calcPercent >= percentGapper and abs(gap) >= minPrice:
                on_gappers.append((i, df.iloc[i].close, df.iloc[i].name))
                on_gappers.append((i, df.iloc[i+1].open, df.iloc[i+1].name))
        return on_gappers

    # talib expoential moving average

    @staticmethod
    def Ema(df: pd.DataFrame, params: dict = None):
        days = 30 if 'days' not in params else params['days']
        ema = abstract.EMA(df, timeperiod=days)
        return ema.to_json()
        # ema = talib.exponential_moving_average(df['close'], timeperiod=days,
        #                                        nbdev=smoothing)
        # return ema

    # Create VWAP function
    @staticmethod
    def Vwap(df: pd.DataFrame, params: dict = None):
        v = df['volume'].values
        tp = (df['low'] + df['close'] + df['high']).div(3).values
        return df.assign(vwap=(tp * v).cumsum() / v.cumsum())

    @staticmethod
    def CandleStickPattern(df: pd.DataFrame, params: dict = None):
        patterns = params['patterns'].split(
            ',') if 'patterns' in params else []
        for pattern in patterns:
            pattern_function = getattr(talib, pattern)
            results = []
            try:
                result = pattern_function(
                    df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]
                if last > 0:
                    results.append(pattern, 'bullish')
                elif last < 0:
                    results.append(pattern, 'bearish')
                # else:
                #     stocks[symbol][pattern] = None
            except:
                pass
        return pattern

    @staticmethod
    def PriceMomentum(df: pd.DataFrame, params: dict = None):
        periods = params['periods'] if 'periods' in params else 5
        output = abstract.MOM(df['close'], timeperiod=periods)
        return output
