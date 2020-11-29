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
        self.name = name
        ex_class = getattr(ccxt, name)
        self.ex = ex_class()

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, float]:
        res = self.ex.fetch_ticker(symbol=symbol)
        #print(res)
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
    tickers = []
    for name, symbols in targets.items():

        if name in ex_classes:
            ex = ex_classes[name]()

        for s in symbols:
            try:

                t = ex.get_ticker(s['symbol'])
                tickers.append(t)

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

    btcjpy = [t for t in tickers if t['symbol'] == 'BTC/JPY']

    min_ask = find_min_ask(btcjpy)
    max_ask = find_max_ask(btcjpy)
    min_bid = find_min_bid(btcjpy)
    max_bid = find_max_bid(btcjpy)

    print('Min Ask: ', min_ask[0], min_ask[1])
    print('Max Ask: ', max_ask[0], max_ask[1])
    print('Min Bid: ', min_bid[0], min_bid[1])
    print('Max Bid: ', max_bid[0], max_bid[1])

    ask_dif = max_ask[1] - min_ask[1]
    bid_dif = max_bid[1] - min_bid[1]
    print(f'Ask diff: {ask_dif}, Bid diff: {bid_dif}')

    if max_bid[1] > min_ask[1]:
        print(f'Found a arbitrage chance: {max_bid[1] - min_ask[1]}')
        points.append({
            'measurement': 'price_diff',
            'tags': {
                'symbol': 'BTC/JPY'
            },
            'fields': {
                'value': max_bid[1] - min_ask[1],
                'buy_exchange': min_ask[0],
                'buy_price': min_ask[1],
                'sell_exchange': max_bid[0],
                'sell_price': max_bid[1],
            }
        })

    client = InfluxDBClient(dbhost, dbport, dbuser, dbpass, dbname)
    client.write_points(points)


def find_min_ask(tickers):
    name  = ''
    p = 0
    for t in tickers:
        if not p or t['ask'] < p:
            name = t['name']
            p = t['ask']
    return (name, p,)


def find_max_ask(tickers):
    name  = ''
    p = 0
    for t in tickers:
        if not p or t['ask'] > p:
            name = t['name']
            p = t['ask']
    return (name, p,)


def find_min_bid(tickers):
    name  = ''
    p = 0
    for t in tickers:
        if not p or t['bid'] < p:
            name = t['name']
            p = t['bid']
    return (name, p,)


def find_max_bid(tickers):
    name  = ''
    p = 0
    for t in tickers:
        if not p or t['bid'] > p:
            name = t['name']
            p = t['bid']
    return (name, p,)


if __name__ == '__main__':
    main()

