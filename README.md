c3 (Cryptocurrency Collector)
=============================

![.github/workflows/cron.yml](https://github.com/mitsutoshi/c3/workflows/.github/workflows/cron.yml/badge.svg)

c3 is collecting tool that getting and storing cryptocurrency price.

## How to install

### pip

```
pip install -r requirements.txt
```

### pipenv

```
pipenv install -r requirements.txt
```

## How to run on local machine

1. Start pipenv.

    ```
    pipenv shell
    ```

2. Run `c3.py`.

    ```sh
    python c3.py
    ```

## Database Layout

### InfluxDB

#### database

cryptocurrency

#### Measurement

prices

#### Tags

|Name|Value|
|---|---|
|exchange|exchange name (e.g. bitmex, bitflyer)|
|symbol|cryptocurrency symbol name (e.g. .BXBT, FX_BTC_JPY)|
|currency|currency name (e.g. USD, JPY)|

#### Values

|Name|Value|
|---|---|
|value|price of cryptocurrency|


