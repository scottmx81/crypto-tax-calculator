"""
Crypto tax calculator.
"""
import argparse
from decimal import Decimal

from calculator import Calculator, CSVReader, read_exchange_rates


DEFAULT_BASE_CURRENCY = 'cad'


def main():
    """
    Main entry point from CLI.
    """
    args = parse_args()

    trades = read_trade_files(args.trades)
    exchange_rates = read_exchange_rates(args.exchange_rates)

    calculator = Calculator(
        trades,
        exchange_rates,
        args.base_currency,

    )
    result = calculator.calculate(
        initial_acb=args.initial_acb,
        initial_units_held=args.initial_units_held,
    )

    print_result(result)


def parse_args():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--base-currency',
        default=DEFAULT_BASE_CURRENCY,
        help="The base currency for calculations",
        type=str,
    )
    parser.add_argument(
        '--exchange-rates',
        default=DEFAULT_BASE_CURRENCY,
        help="Path to CSV file containing historical exchange rates",
        type=str,
    )
    parser.add_argument(
        '--initial-acb',
        default=Decimal('0'),
        help='The initial acb if prior trade history is not available',
        type=Decimal,
    )
    parser.add_argument(
        '--initial-units-held',
        default=Decimal('0'),
        help='The initial units held if prior trade history is not available',
        type=Decimal,
    )
    parser.add_argument(
        'trades',
        help='Path to CSV file(s) containing trade history',
        type=str,
        nargs='+',
    )
    return parser.parse_args()


def read_trade_files(filenames):
    """
    Read the trade CSV files.
    """
    trades = []

    for filename in filenames:
        trades += read_trade_file(filename)

    return trades


def read_trade_file(filename):
    """
    Read the trades from a single CSV file.
    """
    csv_reader = CSVReader()
    return csv_reader.read_trades(filename)


def print_result(result):
    """
    Print the calculation results.
    """
    print(
        'Action,Major,Minor,Amount,Rate,Date,Adjusted Cost Base,Units Held,'
        'Capital Gain,Total Capital Gains,Exchange Rate'
    )

    for event in result['events']:
        print('{},{},{},{},{},{},{},{},{},{},{}'.format(
            event['action'],
            event['major'],
            event['minor'],
            event['amount'],
            event['rate'],
            event['dt'],
            event['acb'],
            event['units_held'],
            event['capital_gain'],
            event['capital_gains'],
            event['exchange_rate'],
        ))

    print('-------')
    print('ACB,{}'.format(result['acb']))
    print('Sum ACB Dispositions,{}'.format(
        result['sum_acb_dispositions']
    ))
    print('Units Held,{}'.format(result['units_held']))
    print('Buys,${}'.format(result['buys']))
    print('Sells,${}'.format(result['sells']))
    print('Capital gains,${}'.format(result['capital_gains']))


if __name__ == "__main__":
    main()
