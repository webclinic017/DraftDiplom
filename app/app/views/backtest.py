from rest_framework.decorators import api_view
import logging
from django.http import JsonResponse
from datetime import datetime
from app.models import Backtest
import requests
from dataclasses import dataclass
import pandas as pd
import os
from django.conf import settings
from app.backtrading import execute

logger = logging.getLogger("script")

symbols_list = ["XBTUSD", "ADAM20", "BCHM20", "EOSM20", "ETHUSD"]
bitmex_host = "https://www.bitmex.com/api/v1"

@dataclass
class QuoteRaw:
    date: str
    open: str
    close: str
    high: str
    low: str
    adj_close: str
    volume: str


@api_view(['POST'])
def start_execution(request):
    try:
        backtest = prepare_execution(request)
        quotes_list = get_bitmex_data(backtest)
        write_csv(backtest, quotes_list)

        try:
            file_name = f"{backtest.id}.csv"
            result = execute(backtest.start_time, backtest.end_time, os.path.join(settings.STATIC_TEMP, file_name))
        except Exception as err:
            raise Exception(f"Failed while executing algorithm: {err}")

        backtest.result = result[0]
        backtest.save()

        return JsonResponse({"percent": f"{result[0]}", "trades": result[1], "closes": result[2]}, status=200)
    except Exception as err:
        logger.info(f"Failed to execute request: {err}")
        return JsonResponse({"message": f"{err}"}, status=400)

def get_bitmex_data(backtest):
    try:
        response = requests.get(f"{bitmex_host}/trade/bucketed?symbol={backtest.symbol}&binSize={backtest.bin_size}"
                           f"&startTime={backtest.start_time}&endTime={backtest.end_time}").json()
    except Exception as err:
        raise Exception(f"Failed to execute request to Bitmex: {err}")

    try:
        quotes_list = []
        for quote in response:
            quotes_list.append(
                QuoteRaw(
                    date = datetime.strptime(quote['timestamp'][:-1], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d"),
                    open = quote['open'],
                    close = quote['close'],
                    high = quote['high'],
                    low = quote['low'],
                    adj_close = quote['close'],
                    volume = quote['volume'],
                ))
    except Exception as err:
        raise Exception(f"Failed to parse Bitmex response: {err}")
    return quotes_list



def write_csv(backtest, quotes_list):
    try:
        data = {
            'Date': list(map(lambda x: x.date, quotes_list)),
            'Open': list(map(lambda x: x.open, quotes_list)),
            'Close': list(map(lambda x: x.close, quotes_list)),
            'High': list(map(lambda x: x.high, quotes_list)),
            'Low': list(map(lambda x: x.low, quotes_list)),
            'Adj Close': list(map(lambda x: x.adj_close, quotes_list)),
            'Volume': list(map(lambda x: x.volume, quotes_list))
        }
        df = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        file_name = f"{backtest.id}.csv"
        df.to_csv(os.path.join(settings.STATIC_TEMP, file_name), index=False, header=True)
    except Exception as err:
        raise Exception(f"Failed to write to csv file: {err}")


def prepare_execution(request):
    try:
        start_time = validate_date(request.data['startTime'])
        end_time = validate_date(request.data['endTime'])
        symbol = validate_symbol(request.data['symbol'])
        bin_size = validate_bin_size(request.data['binSize'])
        strategy = validate_strategy(request.data['strategy'])
        check_date_range(start_time, end_time)
    except Exception as err:
        raise Exception(f"Failed to parse request data: {err}")

    try:
        backtest = Backtest.objects.create(
            symbol=symbol,
            strategy = strategy,
            bin_size = bin_size,
            start_time = start_time,
            end_time = end_time,
        )
        logger.info(f"Successfully prepared request parsing: {backtest}")
        return backtest
    except Exception as err:
        logger.error(f"Failed to create backtest object before any execution: {err}")
        raise Exception(f"Failed to create backtest object before any execution: {err}")

def check_date_range(start, end):
    delta = end - start
    if delta.days > 120:
        raise Exception("invalid date range, must be lower than 120 days")

def validate_date(line):
    try:
        return datetime.strptime(line, "%Y-%m-%d")
    except:
        raise Exception("invalid date " + line)

def validate_symbol(symbol):
    if symbol in symbols_list:
        return symbol
    raise Exception("invalid symbol " + symbol)

def validate_bin_size(bin_size):
    if bin_size == "1d":
        return bin_size
    raise Exception("invalid binSize " + bin_size)

def validate_strategy(strategy):
    if strategy == "Macrossover":
        return strategy
    raise Exception("invalid strategy " + strategy)