"""
Crypto Tax Calculator.
"""
from copy import deepcopy
import csv
from datetime import datetime
from decimal import Decimal


def read_exchange_rates(filename):
    """
    Read exchange rates from CSV.
    """
    exchange_rates = {}

    with open(filename, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if not row['date'] in exchange_rates:
                exchange_rates[row['date']] = {}
                exchange_rates[row['date']][row['currency']] = \
                    Decimal(row['rate'])

    return exchange_rates


class CSVReader():
    """
    Reads in the CSV files from the exchanges.
    """
    def read_trades(self, filename):
        """
        Read the trades from the CSV file.
        """
        trades = []

        with open(filename, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row['major'] != 'eth' and row['minor'] != 'eth':
                    continue

                trade = {
                    'type': row['type'],
                    'major': row['major'],
                    'minor': row['minor'],
                    'amount': Decimal(row['amount']),
                    'rate': Decimal(row['rate']),
                    'value': Decimal(row['value']),
                    'total': Decimal(row['total']),
                    'dt': datetime.fromtimestamp(float(row['timestamp'])),
                    'timestamp': float(row['timestamp']),
                }

                if trade['dt'] > datetime(2018, 1, 1, 0, 0, 0):
                    continue

                trades.append(trade)

        return trades


class Calculator():
    """
    Tax calculator for crypto trades.
    """
    def __init__(self, trades=None, exchange_rates=None, base_currency='cad'):
        self.trades = deepcopy(trades) if trades else []
        self.exchange_rates = exchange_rates if exchange_rates else {}
        self.base_currency = base_currency

    def calculate(self, initial_acb=None, initial_units_held=None):
        """
        Perform the calculations.
        """
        acb = initial_acb if initial_acb is not None else Decimal('0')
        units_held = initial_units_held \
            if initial_units_held is not None else Decimal('0')
        sum_acb_dispositions = Decimal('0')
        capital_gains = Decimal('0')
        buys = Decimal('0')
        sells = Decimal('0')

        trades = self.trades
        trades.sort(key=lambda trade: trade['timestamp'])

        self.convert_currency(trades, self.exchange_rates)

        events = []

        for trade in trades:
            if trade['type'] == 'buy':
                acb = acb + trade['value']
                units_held += trade['total']

                buys += trade['value']
                events.append({
                    'action': 'Buy',
                    'major': trade['major'],
                    'minor': trade['minor'],
                    'amount': trade['amount'],
                    'rate': trade['rate'],
                    'dt': trade['dt'],
                    'acb': acb,
                    'units_held': units_held,
                    'capital_gain': '',
                    'capital_gains': '',
                    'exchange_rate': trade['exchange_rate'],
                })

            if trade['type'] == 'sell':
                capital_gain = \
                    (trade['total']) - ((acb / units_held) * trade['amount'])
                capital_gains += capital_gain
                sum_acb_dispositions += ((acb / units_held) * trade['amount'])

                acb = acb * ((units_held - trade['amount']) / units_held)
                units_held -= trade['amount']

                sells += trade['value']

                events.append({
                    'action': 'Sell',
                    'major': trade['major'],
                    'minor': trade['minor'],
                    'amount': trade['amount'],
                    'rate': trade['rate'],
                    'dt': trade['dt'],
                    'acb': acb,
                    'units_held': units_held,
                    'capital_gain': capital_gain,
                    'capital_gains': capital_gains,
                    'exchange_rate': trade['exchange_rate'],
                })

        return {
            'events': events,
            'acb': acb,
            'sum_acb_dispositions': sum_acb_dispositions,
            'units_held': units_held,
            'buys': buys,
            'sells': sells,
            'capital_gains': capital_gains,
        }

    def convert_currency(self, trades, exchange_rates):
        """
        Convert the foreign fiat values into the base currency using
        the given exchange rates.
        """
        for trade in trades:
            if trade['minor'] == self.base_currency:
                trade['exchange_rate'] = 1
            else:
                date_string = trade['dt'].strftime('%Y/%m/%d')
                trade['exchange_rate'] = \
                    exchange_rates[date_string][trade['minor']]
                trade['rate'] = trade['rate'] / trade['exchange_rate']
                trade['value'] = trade['value'] / trade['exchange_rate']
                if trade['type'] == 'sell':
                    trade['total'] = trade['total'] / trade['exchange_rate']
