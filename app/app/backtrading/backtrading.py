from datetime import datetime
import logging
import backtrader as bt
from dataclasses import dataclass
import json

logger = logging.getLogger("algorithm")

class Trade:
    def __init__(self, date, title, price):
        self.date = date
        self.title = title
        self.price = price

    def dump(self):
        return {
            'date': self.date,
            'title': self.title,
            'price': self.price
        }

class DayClose:
    def __init__(self, date, price):
        self.date = date
        self.price = price

    def dump(self):
        return {
            'date': self.date,
            'price': self.price
        }

trades_list = []
closes_list = []


class PrintClose(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close

    def log(self, price=None):
        date = self.datas[0].datetime.date(0).isoformat()
        logger.info('%s, %s, %s' % (date, "day close:", price))
        closes_list.append(DayClose(date = date, price = price))

    def next(self):
        self.log('%.2f' % self.dataclose[0])

class MAcrossover(bt.Strategy):
    params = (('pfast', 10), ('pslow', 20),)

    def log(self, txt, price=None):
        date = self.datas[0].datetime.date(0).isoformat()
        logger.info('%s, %s, %s' % (date, txt, price))
        trades_list.append(Trade(date = date, title = txt, price = price))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pfast)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED', '%.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log('BUY CREATE', '%.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('SELL EXECUTED', '%.2f' % self.dataclose[0])
                self.order = self.close()



def execute(start_date, end_date, path):
    trades_list.clear()
    closes_list.clear()

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MAcrossover)
    cerebro.addstrategy(PrintClose)

    data = bt.feeds.YahooFinanceCSVData(
        dataname=path,
        fromdate=datetime(start_date.year, start_date.month, start_date.day),
        todate=datetime(end_date.year, end_date.month, end_date.day),
    )

    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.SizerFix, stake=3)
    start_portfolio_value = cerebro.broker.getvalue()

    cerebro.run(runonce=False)

    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value

    logger.info('Starting Portfolio Value: %.2f' % start_portfolio_value)
    logger.info('Final Portfolio Value: %.2f' % end_portfolio_value)
    percent_result = pnl / (start_portfolio_value / 100)
    return percent_result, [o.dump() for o in trades_list], [c.dump() for c in closes_list]