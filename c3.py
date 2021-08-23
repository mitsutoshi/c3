#! /usr/bin/env python

import sys
import os
from abc import ABCMeta, abstractmethod
from typing import Dict

from influxdb import InfluxDBClient

from config import targets
import exchanges


def arbit(tickers, symbol: str):

    sym = norm_symbol(symbol)
    tkrs = [t for t in tickers if norm_symbol(t['symbol']) == sym]

    min_ask_ex, min_ask_price = find_min_ask(tkrs)
    max_bid_ex, max_bid_price = find_max_bid(tkrs)
    print('Min Ask: ', min_ask_ex, min_ask_price, 'Max Bid: ', max_bid_ex, max_bid_price)

    if max_bid_price > min_ask_price:
        print(f'Found a chance: symbol={sym}, width={(max_bid_price - min_ask_price):.2f}, exchange={min_ask_ex}(ask),{max_bid_ex}(bid)')
        return {
            'measurement': 'price_diff',
            'tags': {
                'symbol': sym
            },
            'fields': {
                'value': max_bid_price - min_ask_price,
                'buy_exchange': min_ask_ex,
                'buy_price': min_ask_price,
                'sell_exchange': max_bid_ex,
                'sell_price': max_bid_price,
            }
        }
    return {}


def main():

    points = []
    tickers = []

    for name, symbols in targets.items():

        # get exchange class
        cls = getattr(exchanges, name.title())
        ex = cls()

        for s in symbols:
            try:
                t = ex.get_ticker(s['symbol'])
                tickers.append(t)
                p = {
                    'measurement': 'prices',
                    'time': t['datetime'],
                    'tags': {
                        'exchange': name,
                        'symbol': norm_symbol(s['symbol']),
                        'coin': s['coin'],
                        'currency': s['currency'],
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

    btcjpy = arbit(tickers, 'BTC/JPY')
    xrpjpy = arbit(tickers, 'XRP/JPY')

    if btcjpy:
        points.append(btcjpy)
    if xrpjpy:
        points.append(xrpjpy) 

    dbhost = os.environ['DB_HOST']
    dbport = os.environ['DB_PORT']
    dbname = os.environ['DB_NAME']
    client = InfluxDBClient(dbhost, dbport, '', '', dbname)
    client.write_points(points)


def find_min_ask(tickers):
    price = min([t['ask'] for t in tickers])
    name = [t['name'] for t in tickers if t['ask'] == price][0]
    return (name, price,)


def find_max_bid(tickers):
    price = max([t['bid'] for t in tickers])
    name = [t['name'] for t in tickers if t['bid'] == price][0]
    return (name, price,)


def norm_symbol(symbol: str) -> str:
    if symbol == 'BTC_JPY':
        return 'BTC/JPY'
    elif symbol == 'ETH_JPY':
        return 'ETH/JPY'
    elif symbol == 'XRP_JPY':
        return 'XEP/JPY'
    return symbol


if __name__ == '__main__':
    main()

