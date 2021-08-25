#! /usr/bin/env python

import sys
import os
import json
from abc import ABCMeta, abstractmethod
from typing import Dict

import requests
from influxdb import InfluxDBClient

from config import targets
import exchanges


def arbit(tickers, coin: str):

    tkrs = [t for t in tickers if coin in t['coin']]

    min_ask_ex, min_ask_price = find_min_ask(tkrs)
    max_bid_ex, max_bid_price = find_max_bid(tkrs)
    print('Min Ask: ', min_ask_ex, min_ask_price, 'Max Bid: ', max_bid_ex, max_bid_price)

    if max_bid_price > min_ask_price:
        print(f'Found a chance: coin={coin}, width={(max_bid_price - min_ask_price):.2f}, exchange={min_ask_ex}(ask),{max_bid_ex}(bid)')
        return {
            'measurement': 'price_diff',
            'tags': {
                'coin': coin
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


def get_rate_usdjpy():
    res = requests.get('https://www.gaitameonline.com/rateaj/getrate')
    if res.status_code == 200:
        body = json.loads(res.text)
        for q in body['quotes']:
            if q['currencyPairCode'] == 'USDJPY':
                return float(q['open'])
    return 0


def main():

    usdjpy = get_rate_usdjpy()
    print(f'USDJPY: {usdjpy}')

    points = []
    tickers = []

    # loop for targets exchange, symbol
    for name, symbols in targets.items():

        # get exchange class
        cls = getattr(exchanges, name.title())
        ex = cls()
        for s in symbols:
            try:

                t = ex.get_ticker(s['symbol'])
                last_jpy = t['last'] * usdjpy if s['currency'] == 'USD' else t['last']
                ask_jpy = t['ask'] * usdjpy if s['currency'] == 'USD' else t['ask']
                bid_jpy = t['bid'] * usdjpy if s['currency'] == 'USD' else t['bid']

                t['coin'] = s['coin']
                t['last_jpy'] = last_jpy
                t['ask_jpy'] = ask_jpy
                t['bid_jpy'] = bid_jpy
                tickers.append(t)

                p = {
                    'measurement': 'prices',
                    'time': t['datetime'],
                    'tags': {
                        'exchange': name,
                        'symbol': s['symbol'],
                        'coin': s['coin'],
                        'currency': s['currency'],
                    },
                    'fields': {
                        'last': t['last'],
                        'ask': t['ask'],
                        'bid': t['bid'],
                        'volume': t['volume'],
                        'last_jpy': last_jpy,
                        'ask_jpy': ask_jpy,
                        'bid_jpy': bid_jpy
                    }
                }
                print(f"{name:10} {s['symbol']:8} {t['last_jpy']:8.0f} {t['ask_jpy']:8.0f} {t['bid_jpy']:8.0f}")
                points.append(p)

            except Exception as e:
                print(e)

    #h1, h2, h3, h4, h5 = 'Name', 'Symbol', 'Last', 'Ask', 'Bid'
    #print(f"{h1:10} {h2:8} {h3:8} {h4:8} {h5:8}")


    b = arbit(tickers, 'BTC')
    e = arbit(tickers, 'ETH')
    x = arbit(tickers, 'XRP')

    if b:
        points.append(b)
    if e:
        points.append(e) 
    if x:
        points.append(x) 

    dbhost = os.environ['DB_HOST']
    dbport = os.environ['DB_PORT']
    dbname = os.environ['DB_NAME']
    client = InfluxDBClient(dbhost, dbport, '', '', dbname)
    client.write_points(points)


def find_min_ask(tickers):
    price = min([t['ask_jpy'] for t in tickers])
    name = [t['name'] for t in tickers if t['ask_jpy'] == price][0]
    return (name, price,)


def find_max_bid(tickers):
    price = max([t['bid_jpy'] for t in tickers])
    name = [t['name'] for t in tickers if t['bid_jpy'] == price][0]
    return (name, price,)


if __name__ == '__main__':
    main()

