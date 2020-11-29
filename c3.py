#! /usr/bin/env python

import sys
import os
from abc import ABCMeta, abstractmethod
from typing import Dict

import ccxt
from influxdb import InfluxDBClient

from config import targets


class Spider(metaclass=ABCMeta):

    def __init__(self, name):
        ex_class = getattr(ccxt, name)
        self.ex = ex_class()

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, float]:
        res = self.ex.fetch_ticker(symbol=symbol)
        #print(res)
        return {
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


ex_classes = {
        'bitflyer': Bitflyer,
        'bitbank': Bitbank,
        'liquid': Liquid,
        'coincheck': Coincheck
        }

Spider.register(Bitflyer)
Spider.register(Bitbank)
Spider.register(Liquid)
Spider.register(Coincheck)

def main():

    dbhost = os.environ['DB_HOST']
    dbport = os.environ['DB_PORT']
    dbname = os.environ['DB_NAME']
    dbuser = os.getenv('DB_USER', '')
    dbpass = os.getenv('DB_PASS', '')

    points = []
    for name, symbols in targets.items():

        if name in ex_classes:
            ex = ex_classes[name]()

        for s in symbols:
            try:
                t = ex.get_ticker(s['symbol'])
                p = {
                    'measurement': 'prices',
                    'time': t['datetime'],
                    'tags': {
                        'exchange': name,
                        'symbol': s['symbol'],
                        'currency': s['currency']
                    },
                    'fields': {
                        'last': t['last'],
                        'ask': t['ask'],
                        'bid': t['bid'],
                        'volume': t['volume']
                    }
                }
                print(p)
                points.append(p)
            except Exception as e:
                print(e)

    client = InfluxDBClient(dbhost, dbport, dbuser, dbpass, dbname)
    client.write_points(points)


if __name__ == '__main__':
    main()

