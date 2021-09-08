from logging import Formatter
from redisPubsub import RedisPublisher
import redis
import json
from redisUtil import KeyName, RedisAccess, StudyScores
from operator import itemgetter


class RedisHash:

    def __init__(self, key, r=None, callback=None):
        self.redis = RedisAccess.connection(r)
        self.callback = callback
        self.key = key

    @property
    def get_key(self):
        return self.key

    def _getAll(self, key):
        return self.redis.hgetall(key)

    def getAll(self):
        return self._getAll(self.key)

    def _add(self, key, symbol, jsondata):
        data = json.dumps(jsondata)
        self.redis.hset(key, symbol, data)
        if (self.callback != None):
            self.callback(symbol, jsondata)

    def add(self, symbol, jsondata):
        return self._add(self.key, symbol, jsondata)

    def delete(self, symbol):
        self.redis.hdel(self.key, symbol)

    def _value(self, key, symbol):
        data = self.redis.hget(key, symbol)
        if data == None:
            return None
        return json.loads(data)

    def value(self, symbol):
        return self._value(self.key, symbol)

    def isSymbolExist(self, symbol):
        return self.redis.hexists(self.key, symbol)


class ThreeBarPlayStack(RedisHash):
    def __init__(self, r=None, unsubCallback=None):
        self.key = KeyName.KEY_THREEBARSTACK
        self.subscribes = {}
        self.unsubscribes = {}
        self.unsubCallback = unsubCallback
        RedisHash.__init__(self, self.key, r)
        self.publisher = RedisPublisher(
            channels=KeyName.EVENT_NEW_CANDIDATES, r=self.redis)

    @property
    def get_subscribes(self):
        return self.subscribes

    @property
    def get_unsubscribes(self):
        return self.unsubscribes

    def openMark(self):
        oneDict = self.getAll()
        for key in oneDict:
            self.unsubscribes[key.decode()] = ''
        self.subscribes = {}

    def addSymbol(self, symbol, jsondata):
        if (not self.isSymbolExist(symbol)):
            self.subscribes[symbol] = symbol
        if symbol in self.unsubscribes:
            self.unsubscribes.pop(symbol)
        self.add(symbol, jsondata)

    def getList(dict):
        return list(map(itemgetter(0), dict.items()))

    def closeMark(self):
        subs = [*self.subscribes.keys()]
        print('SUBS:')
        print(subs)
        unsubs = [*self.unsubscribes.keys()]
        print('UNSUB:')
        print(unsubs)
        if len(unsubs) > 0:
            for unsub in unsubs:
                self.delete(unsub)
                if (self.unsubCallback != None):
                    self.unsubCallback(self.redis, unsub)
        data = {'subscribe': subs, 'unsubscribe': unsubs}
        self.publisher.publish(data)
        self.subscribes = {}
        self.unsubscribes = {}
        oneDict = self.getAll()
        print('CANDIDATES:')
        print(oneDict)


class ThreeBarKeepScore (RedisHash):
    def __init__(self, symbol, r=None):
        self.key = KeyName.KEY_THREEBARSCORE
        RedisHash.__init__(self, self.key, r)
        self.score: StudyScores = StudyScores(self.key, symbol)

    def save(self):
        # data = self.score.serialize_to_string()
        data = self.score.serialize()
        self.add(self.score.Symbol, data)

    def load(self):
        data = self.value(self.score.Symbol)
        self.score.deserialize_from_string(data)


if __name__ == "__main__":
    app = ThreeBarKeepScore('test')
    app.score.Score = 50
    print(app.score)
    app.save()
    bpp = ThreeBarKeepScore('test')
    bpp.load()
    print(bpp.score)
    # app = ThreeBarPlayStack()
    # app.add("AAPL", {'name': 'test', 'data': 'this is text'})
    # myDict = app.redis.hvals('STUDYTHREEBARSTACK')
    # newDict = []
    # for item in myDict:
    #     print(item)
    # data1 = app.value('FANG')
    # print(app.value("AAPL"))
    # print('done')
