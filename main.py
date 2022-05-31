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

    #while True:

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

                p = create_price_point(
                        timestamp=t['datetime'],
                        exchange=name,
                        coin=s['coin'],
                        currency=s['currency'],
                        last=last,
                        ask=ask,
                        bid=bid)

                print(f"{name:10} {s['symbol']:8} {last} {ask} {bid}")
                points.append(p)

            except Exception as e:
                print(e)

    idb.write_points(points)
    #time.sleep(20)


if __name__ == '__main__':
    main()
