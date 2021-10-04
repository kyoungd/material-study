from redisUtil import KeyName, AlpacaAccess, RedisTimeFrame
import pandas as pd
import json
import uuid


class AlpacaDownloader:
    def __init__(self, symbols, period=None, time_length=None):
        self.symbols = symbols
        self.period = self.default_period(period)
        self.time_length = self.default_time_length(time_length)
        self.dataframe = None

    def default_period(self, period):
        if period is None:
            return 'day'
        return period

    def default_time_length(self, time_length):
        if time_length is None:
            switcher = {
                'hour': 21,
                'day': 90,
                'week': 360
            }
            return switcher.get(self.period, 90)
        return time_length

    def timeframe(self, period):
        if period is None:
            return 'day'
        return period

    def convert_time_to_column(self, pd1):
        #        pd1['time'] = pd1.index
        return pd1

    def run(self):
        api = AlpacaAccess.connection()
        barset: pd = api.get_barset(
            self.symbols, self.timeframe(self.period), limit=self.time_length).df
        self.dataframe = self.convert_time_to_column(barset)
        return self.dataframe

    @staticmethod
    def get_filename(file_name=None):
        if (file_name is None):
            file_name = str(uuid.uuid4())
            return file_name, "./pickled/" + file_name + ".pkl"
        return "", "./pickled/" + file_name + ".pkl"

    def save_dataframe(self):
        filename_only, df_file = AlpacaDownloader.get_filename()
        if self.dataframe is None:
            return ""
        self.dataframe.to_pickle(df_file)
        return filename_only

    @staticmethod
    def load_dataframe(filename_only):
        _, df_file = AlpacaDownloader.get_filename(filename_only)
        return pd.read_pickle(df_file)

    @staticmethod
    def load_from_json(json_data):
        data = pd.read_json(json_data, orient='records')
        return data
