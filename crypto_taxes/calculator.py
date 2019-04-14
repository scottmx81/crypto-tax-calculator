"""
Crypto Tax Calculator.
"""
from copy import deepcopy
import csv
from datetime import date, datetime
from decimal import Decimal


def is_target_tax_year(trade_date, tax_year):
    """
    Check if the trade date is within the target tax year.
    """
    year_start = datetime(tax_year, 1, 1, 0, 0, 0)
    next_year_start = datetime(tax_year+1, 1, 1, 0, 0, 0)
    return year_start <= trade_date < next_year_start


class CSVReader():
    """
    Reads in the CSV files from the exchanges.
    """
    def read_trades(self, filename, target_asset):
        """
        Read the trades from the CSV file.
        """
        trades = []

        with open(filename, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if target_asset not in (row['major'], row['minor']):
                    continue

                trade = {
                    'type': row['type'],
                    'major': row['major'].lower(),
                    'minor': row['minor'].lower(),
                    'amount': Decimal(row['amount']),
                    'rate': Decimal(row['rate']),
                    'value': Decimal(row['value']),
                    'total': Decimal(row['total']),
                    'dt': datetime.fromtimestamp(float(row['timestamp'])),
                    'timestamp': float(row['timestamp']),
                }

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

    def calculate(
            self,
            tax_year=None,
            initial_acb=None,
            initial_units_held=None
    ):
        """
        Perform the calculations.
        """
        tax_year = tax_year if tax_year is not None else date.today().year
        acb = initial_acb if initial_acb is not None else Decimal('0')
        units_held = initial_units_held \
            if initial_units_held is not None else Decimal('0')
        sum_acb_dispositions = Decimal('0')
        capital_gains = Decimal('0')
        buys = Decimal('0')
        sells = Decimal('0')

        events = []

        for trade in self.trades:
            if not is_target_tax_year(trade['dt'], tax_year):
                continue

            self.convert_currency(trade)

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

    def convert_currency(self, trade):
        """
        Convert the foreign fiat values into the base currency using
        the given exchange rates.
        """
        if trade['minor'] == self.base_currency:
            trade['exchange_rate'] = 1
            return

        date_string = trade['dt'].strftime('%Y/%m/%d')
        trade['exchange_rate'] = \
            self.exchange_rates[date_string][trade['minor']]
        trade['rate'] = trade['rate'] / trade['exchange_rate']
        trade['value'] = trade['value'] / trade['exchange_rate']
        if trade['type'] == 'sell':
            trade['total'] = trade['total'] / trade['exchange_rate']
