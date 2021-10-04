from flask import Flask
from flask_cors import CORS
import json
from flask import request, jsonify
import sys
import os
from technicalAnalysis import TechnicalAnalysis
from taKeyLevels import StudyKeyLevels
from taDownloadAlpaca import AlpacaDownloader

app = Flask(__name__)
CORS(app)


@app.route("/sentiment", methods=['POST'])
def score():
    text = request.get_json()['text']
    # return(predict(text, model).to_json(orient='records'))


def getAlpacaDataData(symbols, period, length):
    alp = AlpacaDownloader(symbols, period, length)
    data = alp.run()
    result = alp.json_dump()
    return result


def getQueryString(request, name):
    try:
        return request.args.get(name)
    except:
        return None


@app.route("/study/market-data", methods=['GET'])
def getMarketData():
    stocks = request.args.get('symbols')
    symbols = stocks.split(',')
    period = getQueryString(request, 'period')
    length = getQueryString(request, 'length')
    alp = AlpacaDownloader(symbols, period, length)
    data = alp.run()
    result = alp.save_dataframe()
    return result


def getSymbolsAndData(request):
    filename_only = getQueryString(request, 'filename')
    data = AlpacaDownloader.load_dataframe(filename_only)

    # extract symbols from dataframe
    keys = data.columns.values.tolist()
    stocks = list(next(zip(*keys)))
    # unique items in stocks
    symbols = list(set(stocks))
    return symbols, data


def callGetMethod(request, callback=None):
    if callback is None:
        return False
    # query string as a dictionary
    params = request.args.to_dict()
    symbols, data = getSymbolsAndData(request)
    results = []
    for symbol in symbols:
        stock = data[symbol]
        result = callback(stock, params)
        results.append({'symbol': symbol, 'data': result})
    return json.dumps(results)


@app.route("/study/overnight-gappers", methods=['GET'])
def overnightGappers():
    result = callGetMethod(request, StudyKeyLevels.OvernightGappers)
    return result


@app.route("/study/ema", methods=['GET'])
def getEma():
    result = callGetMethod(request, TechnicalAnalysis.Ema)
    return result


@app.route("/study/vwap", methods=['GET'])
def getVwap():
    result = callGetMethod(request, TechnicalAnalysis.Vwap)
    return result


@app.route("/study/key-levels", methods=['GET'])
def getKeyLevels():
    # symbols, data = parseJsonBody(request)
    symbols, data = getSymbolsAndData(request)

    r = StudyKeyLevels(symbols, data)
    data = r.run()
    return json.dumps(data)


@app.route("/live/ping", methods=['GET'])
def live():
    return 'OK'


if __name__ == '__main__':
    hostEnv = os.getenv('HOST_URL', '0.0.0.0')
    portEnv = os.getenv('HOST_PORT', 8102)
    app.run(host=hostEnv, port=portEnv, debug=False, threaded=True)
    # app.run(host='0.0.0.0', port=8102, debug=False, threaded=True)
