#! /usr/env python

import sys
import os
import ccxt
from influxdb import InfluxDBClient
from config import targets


def main():

    dbhost = os.environ['DB_HOST']
    dbport = os.environ['DB_PORT']
    dbname = os.environ['DB_NAME']
    dbuser = os.getenv('DB_USER', '')
    dbpass = os.getenv('DB_PASS', '')

    points = []
    for name, symbols in targets.items():
        ex_class = getattr(ccxt, name)
        ex = ex_class()
        for s in symbols:
            res = ex.fetch_ticker(symbol=s['symbol'])
            points.append({
                'measurement': 'prices',
                'time': res['datetime'],
                'tags': {
                    'exchange': name,
                    'symbol': s['symbol'],
                    'currency': s['currency']
                },
                'fields': {
                    'value': res['last']
                }
            })

    client = InfluxDBClient(dbhost, dbport, dbuser, dbpass, dbname)
    client.write_points(points)


if __name__ == '__main__':
    main()
