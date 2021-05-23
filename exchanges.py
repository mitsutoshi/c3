import json
from abc import ABCMeta, abstractmethod
from typing import Dict
import ccxt
import requests
from influxdb import InfluxDBClient
from config import targets


class Spider(metaclass=ABCMeta):

    def __init__(self, name):
        self.name = name
        ex_class = getattr(ccxt, name)
        self.ex = ex_class()

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, float]:
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


class Bitflyer(Spider):

    def __init__(self):
        super().__init__('bitflyer')

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        return super().get_ticker(symbol)


class Bitbank(Spider):

    def __init__(self):
        super().__init__('bitbank')

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        return super().get_ticker(symbol)


class Liquid(Spider):

    def __init__(self):
        super().__init__('liquid')

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        return super().get_ticker(symbol)


class Coincheck(Spider):

    def __init__(self):
        super().__init__('coincheck')

    def get_ticker(self, symbol: str) -> Dict[str, float]:
        return super().get_ticker(symbol)


class Gmo(Spider):

    def __init__(self):
        self.__name = 'gmo'

    def get_ticker(self, symbol: str) -> Dict[str, float]:
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


ex_classes = {
        'bitflyer': Bitflyer,
        'bitbank': Bitbank,
        'liquid': Liquid,
        'coincheck': Coincheck,
        'gmo': Gmo,
        }

Spider.register(Bitflyer)
Spider.register(Bitbank)
Spider.register(Liquid)
Spider.register(Coincheck)
Spider.register(Gmo)
