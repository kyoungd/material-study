import logging
import time
import sys
from redisUtil import AlpacaStreamAccess
from redisPubsub import StreamBarsPublisher, StreamBarsSubscriber
from redisTSCreateTable import CreateRedisStockTimeSeriesKeys
from redisTSBars import RealTimeBars
from datetime import datetime
import time
import alpaca_trade_api as alpaca
from alpaca_trade_api.stream import Stream
from redisHash import ActiveBars

# from alpaca_trade_api.common import URL
# from redistimeseries.client import Client
# from alpaca_trade_api.rest import REST
# from redisTSBars import RealTimeBars


# MinuteBarStream
# This handles the real-time flow of data, 1 minute bars.
# Aplpaca updates data every minute, but it only sends data that
# has changed.  This makes the data table disjointed, but it is efficient.

class MinuteBarStream:
    log = None
    # when the data is pushed, it is pushed to redis pub/sub table.
    subscriber: StreamBarsSubscriber = None
    publisher: StreamBarsPublisher = None
    # Alpaca Real-Time stream data connection
    stream: Stream = None
    # a connection to RealTimeBars class that handles redis time series
    # data.  All real-time data (real time, 1 Min, 2 Min, 5 MIn) are
    # stored using the class.
    # Also, the data is automaticlaly expired.  Perk of time series.
    rtb: RealTimeBars = None
    # a connection to ActiveBars class.  It stores all symbols that were
    # updated in the last minute.  I do not have to go through the all
    # symbols, and only go through changed ones.
    ab: ActiveBars = None

    @staticmethod
    def init(conn: Stream = None):
        #
        # Connect to Redis TimeSeries
        # Connect to Redis Pub/Sub to handle Stream Bar data
        # Connect to Alpaca Real-Time stream
        # Connect to RealTimeBars class to store Real-Time data to redis time series
        # Connect to ActiveBars class to store active symbols
        #
        MinuteBarStream.log = logging.getLogger(__name__)
        MinuteBarStream.subscriber = StreamBarsSubscriber()
        MinuteBarStream.subscriber.start()
        MinuteBarStream.publisher = StreamBarsPublisher()
        if (conn == None):
            MinuteBarStream.stream = AlpacaStreamAccess.connection()
        else:
            MinuteBarStream.stream = conn
        if (MinuteBarStream.rtb == None):
            MinuteBarStream.rtb = RealTimeBars()
        if MinuteBarStream.ab == None:
            MinuteBarStream.ab = ActiveBars()

# you could leave out the status to also get the inactive ones
# https://forum.alpaca.markets/t/how-do-i-get-all-stocks-name-from-the-market-into-a-python-list/2070/2
# https://alpaca.markets/docs/api-documentation/api-v2/assets/#asset-entity

    # If connection to the Alapaca stream is lost,
    # this will reconnect.  It has known to happen.
    @staticmethod
    def run_connection(conn):
        try:
            conn.run()
        except Exception as e:
            print(f'Exception from websocket connection: {e}')
        finally:
            print("Trying to re-establish connection")
            time.sleep(3)
            MinuteBarStream.run_connection(conn)

    # This handles one minute bar data.  It is called by the Alpaca
    # stream. It adds to the redis time series (RealTimeBars), and also adds to the
    # active symbols (ActiveBars).
    @staticmethod
    async def handleBar(bar):
        # print('bar: ', bar)
        # bar['t'] = 0

        # direct push to redis
        MinuteBarStream.rtb.redisAdd1Min(bar)
        MinuteBarStream.ab.addSymbol(bar['S'])
        # publish/subscribe
        # MinuteBarStream.publisher.publish(bar)

        # print('bar: ', bar._raw)
        # publisher.publish(bar._raw)

    # This is the main function.  It subscribes to all the symbos
    # in the ActiveBars.  And it runs the stream.

    @staticmethod
    def run():
        logging.basicConfig(level=logging.INFO)
        MinuteBarStream.stream.subscribe_bars(MinuteBarStream.handleBar, '*')

        MinuteBarStream.stream.run()
        MinuteBarStream.run_connection(MinuteBarStream.stream)

        # feed = 'sip'  # <- replace to SIP if you have PRO subscription
        # stream = Stream(AlpacaAccess.ALPACA_API_KEY,
        #                 AlpacaAccess.ALPACA_SECRET_KEY,
        #                 base_url=URL(AlpacaAccess.ALPACA_WS),
        #                 data_feed=feed)
        # stream.subscribe_trade_updates(print_trade_update)
        # stream.subscribe_trades(print_trade, 'AAPL')
        # stream.subscribe_quotes(print_quote, 'IBM')
        # stream.subscribe_quotes(print_quote, 'AAPL')
        # stream.subscribe_quotes(print_quote, 'GOOG')

        # @stream.on_bar('*')
        # async def _(bar):
        #     print('bar: ', bar._raw)
        #     # print('type', type(bar))
        #     publisher.publish(bar._raw)
        #     # RealTimeBars.redis_add_bar(rts, bar)

        # @stream.on_status("*")
        # async def _(status):
        #     print('status', status)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0 and (args[0] == "-t" or args[0] == "-table"):
        app = CreateRedisStockTimeSeriesKeys()
        app.run()
    MinuteBarStream.init()
    MinuteBarStream.run()
    # test()

    # batch insert
    # execute_values(cursor, "INSERT INTO TEST(id, v1, v2) VALUES [(1,2,3), (4,5,6), (7,8,9)]")

    # how to use pgcopy
    # https://docs.timescale.com/timescaledb/latest/quick-start/python/#step-instantiate-a-copymanager-with-your-target-table-and-column-definition


# def test():
#     print('start')
#     data1 = {'symbol': 'UBER', 'open': 39.4199, 'close': 39.49, 'high': 39.5322, 'low': 39.4199,
#              'volume': 89278, 'timestamp': 1629470280000000000, 'trade_count': 618, 'vwap': 39.481653}
#     MinuteBarStream.publisher.publish(data1)
#     data2 = {'symbol': 'UBER', 'open': 39.5199, 'close': 39.59, 'high': 39.6322, 'low': 39.4199,
#              'volume': 89278, 'timestamp': 1629470290000000000, 'trade_count': 618, 'vwap': 39.481653}
#     MinuteBarStream.publisher.publish(data2)
#     data3 = {'symbol': 'UBER', 'open': 39.6199, 'close': 39.69, 'high': 39.7322, 'low': 39.4199,
#              'volume': 89278, 'timestamp': 1629470300000000000, 'trade_count': 618, 'vwap': 39.481653}
#     MinuteBarStream.publisher.publish(data3)
#     data4 = {'symbol': 'UBER', 'open': 39.7199, 'close': 39.79, 'high': 39.8322, 'low': 39.4199,
#              'volume': 89278, 'timestamp': 1629470310000000000, 'trade_count': 618, 'vwap': 39.481653}
#     MinuteBarStream.publisher.publish(data4)
#     data5 = {'symbol': 'UBER', 'open': 39.8199, 'close': 39.89, 'high': 39.9322, 'low': 39.4199,
#              'volume': 89278, 'timestamp': 1629470320000000000, 'trade_count': 618, 'vwap': 39.481653}
#     MinuteBarStream.publisher.publish(data5)
#     print('done')
