from numpy import string_
from redisHash import RedisHash
from redisUtil import KeyName, AlpacaAccess
from datetime import date
import alpaca_trade_api as alpaca
import pandas as pd
from technicalAnalysis import TechnicalAnalysis


class StudyKeyLevels():

    def __init__(self, symbols, dataframe):
        self.symbols = symbols
        self.dataframe = dataframe

    def isToday(self, onedate):
        today = date.today()
        # datetime to date only
        date1 = date(today.year, today.month, today.day)
        date2 = date(onedate.year, onedate.month, onedate.day)
        return date1 == date2

    def run(self):
        # if super().isSymbolExist(symbol):
        #     data1 = super().value(symbol)
        #     keylevels = json.loads(data1)
        #     return keylevels
        pd2: pd = self.dataframe
        keylevels = []
        for symbol in self.symbols:
            data = pd2[symbol]
            kl = TechnicalAnalysis.KeyLevels(data)
            dataset = (symbol, kl)
            keylevels.append(dataset)
        return keylevels


if __name__ == "__main__":
    r = StudyKeyLevels()
    data = r.run('AAPL,FB')
    print(data)


# from support_resistance_line import SupportResistanceLine
# import numpy as np
# import json

# # https://pypi.org/project/support-resistance-line/


# # Generate a random series
# sr = pd.Series(np.random.random(size=250))
# # ... moving avg to make it more trending
# sr = sr.rolling(50).mean().dropna()

# # Init. Index will be ignored
# srl = SupportResistanceLine(sr, kind='support')

# # Plot the best 3 support lines
# srl.plot_top_lines()
# # Plot the best 3 resistance lines
# srl.twin.plot_top_lines()

# # Plot the best support & resistance lines
# srl.plot_both()

# # View the logic steps if you want
# srl.plot_steps()
