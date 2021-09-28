# https://raposa.trade/trade-rsi-divergence-python/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.signal import argrelextrema
from collections import deque


# def getData(self):
#     data = yf.download(self.symbol, self.start, self.end)
#     data['diff_close'] = data['Close'] - data['Close'].shift(1)
#     data['gain'] = np.where(data['diff_close'] > 0, data['diff_close'], 0)
#     data['loss'] = np.where(data['diff_close'] < 0,
#                             np.abs(data['diff_close']), 0)
#     data[['init_avg_gain', 'init_avg_loss']] = data[
#         ['gain', 'loss']].rolling(self.P).mean()
#     avg_gain = np.zeros(len(data))
#     avg_loss = np.zeros(len(data))
#     for i, _row in enumerate(data.iterrows()):

# The logic for each of these is identical,
# we just change out np.greater for np.less in line 9
# and change the inequality sign in line 18 to get the behavior we want.
def getHigherHighs(data: np.array, order=5, K=2):
    '''
    Finds consecutive higher highs in price pattern.
    Must not be exceeded within the number of periods indicated by the width 
    parameter for the value to be confirmed.
    K determines how many consecutive highs need to be higher.
    '''
    # Get highs
    high_idx = argrelextrema(data, np.greater, order=order)[0]  # line #9
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] < highs[i-1]:       # line 18
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def getHigherLows(data: np.array, order=5, K=2):
    high_idx = argrelextrema(data, np.LESS, order=order)[0]  # line #9
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] < highs[i-1]:       # line 18
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())
    return extrema


def getLowerHighs(data: np.array, order=5, K=2):
    high_idx = argrelextrema(data, np.greater, order=order)[0]  # line #9
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] < highs[i-1]:       # line 18
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def getLowerLows(data: np.array, order=5, K=2):
    high_idx = argrelextrema(data, np.less, order=order)[0]  # line #9
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] > highs[i-1]:       # line 18
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def calcRSI(data, P=14):
    data['diff_close'] = data['Close'] - data['Close'].shift(1)
    data['gain'] = np.where(data['diff_close'] > 0, data['diff_close'], 0)
    data['loss'] = np.where(data['diff_close'] < 0,
                            np.abs(data['diff_close']), 0)
    data[['init_avg_gain', 'init_avg_loss']] = data[
        ['gain', 'loss']].rolling(P).mean()
    avg_gain = np.zeros(len(data))
    avg_loss = np.zeros(len(data))
    for i, _row in enumerate(data.iterrows()):
        row = _row[1]
        if i < P - 1:
            last_row = row.copy()
            continue
        elif i == P-1:
            avg_gain[i] += row['init_avg_gain']
            avg_loss[i] += row['init_avg_loss']
        else:
            avg_gain[i] += ((P - 1) * avg_gain[i-1] + row['gain']) / P
            avg_loss[i] += ((P - 1) * avg_loss[i-1] + row['loss']) / P

        last_row = row.copy()

    data['avg_gain'] = avg_gain
    data['avg_loss'] = avg_loss
    data['RS'] = data['avg_gain'] / data['avg_loss']
    data['RSI'] = 100 - 100 / (1 + data['RS'])
    return data


def getHHIndex(data: np.array, order=5, K=2):
    extrema = getHigherHighs(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx < len(data))]


def getLHIndex(data: np.array, order=5, K=2):
    extrema = getLowerHighs(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx < len(data))]


def getLLIndex(data: np.array, order=5, K=2):
    extrema = getLowerLows(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx < len(data))]


def getHLIndex(data: np.array, order=5, K=2):
    extrema = getHigherLows(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx < len(data))]


def getPeaks(data, key='Close', order=5, K=2):
    vals = data[key].values
    hh_idx = getHHIndex(vals, order, K)
    lh_idx = getLHIndex(vals, order, K)
    ll_idx = getLLIndex(vals, order, K)
    hl_idx = getHLIndex(vals, order, K)

    data[f'{key}_highs'] = np.nan
    data[f'{key}_highs'][hh_idx] = 1
    data[f'{key}_highs'][lh_idx] = -1
    data[f'{key}_highs'] = data[f'{key}_highs'].ffill().fillna(0)
    data[f'{key}_lows'] = np.nan
    data[f'{key}_lows'][ll_idx] = 1
    data[f'{key}_lows'][hl_idx] = -1
    data[f'{key}_lows'] = data[f'{key}_highs'].ffill().fillna(0)
    return data


def _calcEMA(P, last_ema, N):
    return (P - last_ema) * (2 / (N + 1)) + last_ema


def calcEMA(data, N):
    # Initialize series
    data['SMA_' + str(N)] = data['Close'].rolling(N).mean()
    ema = np.zeros(len(data))
    for i, _row in enumerate(data.iterrows()):
        row = _row[1]
        if i < N:
            ema[i] += row['SMA_' + str(N)]
        else:
            ema[i] += _calcEMA(row['Close'], ema[i-1], N)
    data['EMA_' + str(N)] = ema.copy()
    return data


def calcReturns(df):
    # Helper function to avoid repeating too much code
    df['returns'] = df['Close'] / df['Close'].shift(1)
    df['log_returns'] = np.log(df['returns'])
    df['strat_returns'] = df['position'].shift(1) * df['returns']
    df['strat_log_returns'] = df['position'].shift(1) * df['log_returns']
    df['cum_returns'] = np.exp(df['log_returns'].cumsum()) - 1
    df['strat_cum_returns'] = np.exp(df['strat_log_returns'].cumsum()) - 1
    df['peak'] = df['cum_returns'].cummax()
    df['strat_peak'] = df['strat_cum_returns'].cummax()
    return df


def RSIDivergenceWithTrendStrategy(data, P=14, order=5, K=2, EMA1=50, EMA2=200):
    '''
    Go long/short on price and RSI divergence.
    - Long if price to lower low and RSI to higher low with RSI < 50
    - Short if price to higher high and RSI to lower high with RSI > 50
    Sell if divergence disappears or if the RSI crosses the centerline, unless
    there is a trend in the same direction.
    '''
    data = getPeaks(data, key='Close', order=order, K=K)
    data = calcRSI(data, P=P)
    data = getPeaks(data, key='RSI', order=order, K=K)
    data = calcEMA(data, EMA1)
    data = calcEMA(data, EMA2)

    position = np.zeros(data.shape[0])
    # position[:] = np.nan
    for i, (t, row) in enumerate(data.iterrows()):
        if np.isnan(row['RSI']):
            continue
        # If no position is on
        if position[i-1] == 0:
            # Buy if indicator to higher high and price to lower high
            if row['Close_lows'] == -1 and row['RSI_lows'] == 1:
                if row['RSI'] < 50:
                    position[i] = 1
                    entry_rsi = row['RSI'].copy()

            # Short if price to higher high and indicator to lower high
            elif row['Close_highs'] == 1 and row['RSI_highs'] == -1:
                if row['RSI'] > 50:
                    position[i] = -1
                    entry_rsi = row['RSI'].copy()

        # If current position is long
        elif position[i-1] == 1:
            if row['RSI'] < 50 and row['RSI'] < entry_rsi:
                position[i] = 1
            elif row[f'EMA_{EMA1}'] > row[f'EMA_{EMA2}']:
                position[i] = 1

        # If current position is short
        elif position[i-1] == -1:
            if row['RSI'] < 50 and row['RSI'] > entry_rsi:
                position[i] = -1
            elif row[f'EMA_{EMA1}'] < row[f'EMA_{EMA2}']:
                position[i] = -1

    data['position'] = position
    return calcReturns(data)
