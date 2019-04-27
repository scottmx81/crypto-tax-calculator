"""
Crypto Tax Calculator.
"""
from copy import deepcopy
import csv
from datetime import date, datetime
from decimal import Decimal

from .exceptions import InsufficientUnitsError
from .parsers import get_parser


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
            parser = get_parser(reader)

            for row in reader:
                trade = parser.parse_row(row)

                if target_asset not in (row['major'], row['minor']):
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
        tabulations = {
            'acb': initial_acb if initial_acb is not None else Decimal('0'),
            'units_held':
                initial_units_held if initial_units_held is not None
                else Decimal('0'),
            'sum_acb_dispositions': Decimal('0'),
            'capital_gains': Decimal('0'),
            'outlays': Decimal('0'),
            'proceeds': Decimal('0'),
        }

        events = []

        for trade in self.trades:
            if not is_target_tax_year(trade['dt'], tax_year):
                continue

            event = self.process_trade(trade, tabulations)
            events.append(event)

        tabulations['events'] = events

        return tabulations

    def process_trade(self, trade, tabulations):
        """
        Perform calculations for an individual trade.
        """
        self.convert_currency(trade)

        if trade['type'] == 'buy':
            capital_gain = self.process_buy(trade, tabulations)
        elif trade['type'] == 'sell':
            capital_gain = self.process_sell(trade, tabulations)

        event = {
            'action': trade['type'],
            'major': trade['major'],
            'minor': trade['minor'],
            'amount': trade['amount'],
            'dt': trade['dt'],
            'acb': tabulations['acb'],
            'rate': trade['rate'],
            'units_held': tabulations['units_held'],
            'exchange_rate': trade['exchange_rate'],
            'capital_gains': tabulations['capital_gains'],
            'capital_gain': capital_gain,
        }

        return event

    def process_buy(self, trade, tabulations):
        """
        Perform calculations for a buy trade.
        """
        # Units of crypto that the exchange took as commission
        commission_units = trade['amount'] - trade['total']

        # The value of the crypto units taken, in the base currency
        commission_fiat = commission_units * trade['rate']

        # The cost of the new crypto units, that we actually received
        cost_new_units = trade['total'] * trade['rate']

        # The previous ACB before this trade
        previous_acb = tabulations['acb']

        # New ACB after buy
        tabulations['acb'] = previous_acb + cost_new_units + commission_fiat

        # Increase units held by the units received after commission taken
        tabulations['units_held'] += trade['total']

        # Increase outlays
        tabulations['outlays'] += cost_new_units + commission_fiat

        return Decimal('0')

    def process_sell(self, trade, tabulations):
        """
        Perform calculations for a sell trade.
        """
        if trade['amount'] > tabulations['units_held']:
            raise InsufficientUnitsError(
                trade['dt'],
                trade['amount'],
                tabulations['units_held'],
            )

        capital_gain = \
            (trade['total']) - (
                (tabulations['acb'] / tabulations['units_held'])
                * trade['amount'])
        tabulations['capital_gains'] += capital_gain
        tabulations['sum_acb_dispositions'] += (
            (tabulations['acb'] / tabulations['units_held'])
            * trade['amount']
        )

        tabulations['acb'] = tabulations['acb'] * (
            (tabulations['units_held'] - trade['amount'])
            / tabulations['units_held']
        )
        tabulations['units_held'] -= trade['amount']
        tabulations['proceeds'] += trade['value']

        return capital_gain

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
