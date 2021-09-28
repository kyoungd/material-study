import logging
import time
import json
from redisUtil import AlpacaStreamAccess, KeyName, SetInterval
from redisPubsub import RedisSubscriber, RedisPublisher
from redisTSCreateTable import CreateRedisStockTimeSeriesKeys
from redis3barScore import StudyThreeBarsScore
import asyncio
import threading

import alpaca_trade_api as alpaca
from alpaca_trade_api.stream import Stream
# from alpaca_trade_api.common import URL
# from redistimeseries.client import Client
# from alpaca_trade_api.rest import REST
# from redisTSBars import RealTimeBars

# Trade schema:
# T - string, message type, always “t”
# S - string, symbol
# i - int, trade ID
# x - string, exchange code where the trade occurred
# p - number, trade price
# s - int, trade size
# t - string, RFC-3339 formatted timestamp with nanosecond precision.
# c - array < string >, trade condition
# z - string, tape


def init():
    try:
        # make sure we have an event loop, if not create a new one
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    global conn
    conn = AlpacaStreamAccess.connection()
    global publisher
    publisher = RedisPublisher(KeyName.EVENT_NEW_CANDIDATES)
    conn.run()


class counter:
    count = 0

    @staticmethod
    def getCount():
        return counter.count

    @staticmethod
    def incCount():
        counter.count = counter.count + 1


def subUnsub():
    subs = []
    unsubs = []
    if (counter.getCount() % 2) == 0:
        subs = ['AAPL', 'FB']
    else:
        unsubs = ['AAPL', 'FB']
    data = {'subscribe': subs, 'unsubscribe': unsubs}
    print(data)
    publisher.publish(data)
    counter.incCount()


def run():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    threading.Thread(target=init).start()

    loop = asyncio.get_event_loop()
    time.sleep(5)  # give the initial connection time to be established
    SetInterval(15, subUnsub)

    print('RUNNING...')
    # while 1:
    #     pass


if __name__ == "__main__":
    run()
