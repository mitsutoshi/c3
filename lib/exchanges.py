import json
from abc import ABCMeta, abstractmethod
import ccxt
import requests
from influxdb import InfluxDBClient
from config import targets


class Spider(metaclass=ABCMeta):

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        ex_class = getattr(ccxt, self.name)
        self.ex = ex_class()

    @abstractmethod
    def get_ticker(self, symbol: str) -> dict[str, float]:
        res = self.ex.fetch_ticker(symbol=symbol)
        return {
                'name': self.name,
                'symbol': symbol,
                'datetime': res['datetime'],
                'last': res['last'],
                'bid': res['bid'],
                'ask': res['ask'],
                'volume': res['baseVolume'],
                }

    @abstractmethod
    def get_tickers(self) -> dict[str, float]:
        res = self.ex.fetch_tickers()
        return {
                'name': self.name,
                'symbol': symbol,
                'datetime': res['datetime'],
                'last': res['last'],
                'bid': res['bid'],
                'ask': res['ask'],
                'volume': res['baseVolume'],
                }

class Bitflyer(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


class Bitbank(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        res = requests.get("https://public.bitbank.cc/tickers")
        tickers = json.loads(res.text)
        data = tickers['data']
        for t in data:
            t.update({'timestamp': int(t['timestamp']) * 1000000})
        return data


class Liquid(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError

class Coincheck(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


class Gmo(Spider):

    def __init__(self):
        self.__name = 'gmo'

    def get_ticker(self, symbol: str) -> dict[str, float]:
        res = requests.get(f'https://api.coin.z.com/public/v1/ticker?symbol={symbol}')
        body = res.json()['data'][0]
        return {
                'name': self.__name,
                'symbol': symbol,
                'datetime': body['timestamp'],
                'last': float(body['last']),
                'bid': float(body['bid']),
                'ask': float(body['ask']),
                'volume': float(body['volume']),
                }

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


class Ftx(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


class Bybit(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)
        #res = requests.get(f'https://api.bybit.com/spot/quote/v1/ticker/24hr')
        #body = res.json()
        #print(body)
        #return {
        #        'name': self.__name,
        #        'symbol': symbol,
        #        'datetime': body['time'],
        #        'last': float(body['lastPrice']),
        #        'bid': float(body['bestBidPrice']),
        #        'ask': float(body['bestAskPrice']),
        #        'volume': float(body['volume']),
        #        }

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


class Binance(Spider):

    def get_ticker(self, symbol: str) -> dict[str, float]:
        return super().get_ticker(symbol)

    def get_tickers(self) -> dict[str, float]:
        raise NotImplementedError


Spider.register(Bitflyer)
Spider.register(Bitbank)
Spider.register(Liquid)
Spider.register(Coincheck)
Spider.register(Gmo)
Spider.register(Ftx)
Spider.register(Bybit)
Spider.register(Binance)
