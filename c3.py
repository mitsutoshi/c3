#! /usr/bin/env python

import os
import json
import time
import requests
from influxdb import InfluxDBClient
from config import targets
from lib import exchanges


idb = InfluxDBClient(
        os.environ['DB_HOST'], os.environ['DB_PORT'], '', '', os.environ['DB_NAME'])


def get_rate_usdjpy():
    res = requests.get('https://www.gaitameonline.com/rateaj/getrate')
    if res.status_code == 200:
        body = json.loads(res.text)
        for q in body['quotes']:
            if q['currencyPairCode'] == 'USDJPY':
                return float(q['open'])
    return 0


def create_price_point(timestamp, exchange, coin, currency, last, ask, bid):
    return {
        'measurement': 'prices',
        'time': timestamp,
        'tags': {
            'exchange': exchange,
            'symbol': f"{coin}/{currency}",
            'coin': coin.upper(),
            'currency': currency.upper(),
        },
        'fields': {
            'last': last,
            'ask': ask,
            'bid': bid,
    }
}


def main():

    while True:

        usdjpy = get_rate_usdjpy()
        print(f'USDJPY: {usdjpy}')

        points = []
        for name, symbols in targets.items():

            cls = getattr(exchanges, name.title())
            ex = cls()

            try:
                tickers = ex.get_tickers()
                for t in tickers:
                    print(t)
                    pair = t['pair'].split('_')
                    p = create_price_point(
                            timestamp=t['timestamp'],
                            exchange=name,
                            coin=pair[0],
                            currency=pair[1],
                            last=float(t['last']),
                            ask=float(t['sell']),
                            bid=float(t['buy']))
                    points.append(p)

                continue

            except NotImplementedError as e:
                print(e)
                pass


            for s in symbols:
                try:

                    t = ex.get_ticker(s['symbol'])

                    last = t['last'] / usdjpy if s['currency'] == 'JPY' else t['last']
                    ask = t['ask'] / usdjpy if s['currency'] == 'JPY' else t['ask']
                    bid = t['bid'] / usdjpy if s['currency'] == 'JPY' else t['bid']
                    last_jpy = int(t['last'] * usdjpy if s['currency'] == 'USD' else t['last'])
                    ask_jpy = int(t['ask'] * usdjpy if s['currency'] == 'USD' else t['ask'])
                    bid_jpy = int(t['bid'] * usdjpy if s['currency'] == 'USD' else t['bid'])

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
                            'last': last,
                            'ask': ask, 'bid': bid,
                            'last_jpy': last_jpy,
                            'ask_jpy': ask_jpy,
                            'bid_jpy': bid_jpy
                        }
                    }

                    print(f"{name:10} {s['symbol']:8} {last} {ask} {bid}")
                    points.append(p)

                except Exception as e:
                    print(e)

        idb.write_points(points)
        print('done')

        time.sleep(20)


#def arbit(tickers, coin: str):
#
#    tkrs = [t for t in tickers if coin in t['coin']]
#
#    min_ask_ex, min_ask_price = find_min_ask(tkrs)
#    max_bid_ex, max_bid_price = find_max_bid(tkrs)
#    print('Min Ask: ', min_ask_ex, min_ask_price, 'Max Bid: ', max_bid_ex, max_bid_price)
#
#    if max_bid_price > min_ask_price:
#        print(f'Found a chance: coin={coin}, width={(max_bid_price - min_ask_price):.2f}, exchange={min_ask_ex}(ask),{max_bid_ex}(bid)')
#        return {
#            'measurement': 'price_diff',
#            'tags': {
#                'coin': coin
#            },
#            'fields': {
#                'value': max_bid_price - min_ask_price,
#                'buy_exchange': min_ask_ex,
#                'buy_price': min_ask_price,
#                'sell_exchange': max_bid_ex,
#                'sell_price': max_bid_price,
#            }
#        }
#    return {}


#def find_min_ask(tickers):
#    price = min([t['ask_jpy'] for t in tickers])
#    name = [t['name'] for t in tickers if t['ask_jpy'] == price][0]
#    return (name, price,)


#def find_max_bid(tickers):
#    price = max([t['bid_jpy'] for t in tickers])
#    name = [t['name'] for t in tickers if t['bid_jpy'] == price][0]
#    return (name, price,)


if __name__ == '__main__':
    main()

