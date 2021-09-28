import json

from numpy import string_
from redisHash import RedisHash
from redisUtil import KeyName, AlpacaAccess
from datetime import date
import alpaca_trade_api as alpaca
import pandas as pd
from technicalAnalysis import TechnicalAnalysis


class StudyKeyLevels(RedisHash):

    def __init__(self, key=None, r=None):
        if key is None:
            key = KeyName.STUDY_KEY_LEVELS
        super().__init__(key, r)

    def isToday(self, onedate):
        today = date.today()
        # datetime to date only
        date1 = date(today.year, today.month, today.day)
        date2 = date(onedate.year, onedate.month, onedate.day)
        return date1 == date2

    def download_historical_data(self, symbol) -> pd:
        api = AlpacaAccess.connection()
        barset = api.get_barset(symbol, 'day', limit=90).df
        return barset

    def run(self, symbols):
        # if super().isSymbolExist(symbol):
        #     data1 = super().value(symbol)
        #     keylevels = json.loads(data1)
        #     return keylevels
        keylevels = []
        pd2: pd = self.download_historical_data(symbols)
        stocks = symbols.split(',')
        for symbol in stocks:
            data = pd2[symbol]
            kl = TechnicalAnalysis.KeyLevels(pd2)
            super().set(symbol, json.dumps(kl))
            keylevels.append(kl)
        return keylevels


if __name__ == "__main__":
    r = StudyKeyLevels()
    data = r.run('AAPL,FB')
    print(data)
