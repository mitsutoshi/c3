c3 (Cryptocurrency Collector)
=============================

c3 is collecting tool that getting and storing cryptocurrency price.

## Target

|Exchange|Symbol|
|---|---|
|bitflyer|FX_BTC_JPY|
|bitmex|.BXBT|

## How to install

### pip

```
pip install -r requirements.txt
```

## How to run on local machine

1. Update `config.py`.

2. Start pipenv.

    ```
    pipenv shell
    ```

3. Run `c3.py`.

    ```sh
    python c3.py
    ```

## Layout

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


