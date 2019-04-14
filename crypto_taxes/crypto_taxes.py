"""
Crypto tax calculator.
"""
import argparse
import csv
from decimal import Decimal
from sys import stderr

from calculator import Calculator, CSVReader


DEFAULT_BASE_CURRENCY = 'cad'
DEFAULT_ASSET = 'btc'


def main():
    """
    Main entry point from CLI.
    """
    args = parse_args()

    trades = read_trade_files(args.trades, args.asset)
    exchange_rates = read_exchange_rates(args.exchange_rates)

    trades.sort(key=lambda trade: trade['timestamp'])

    missing_exchange_rates = find_missing_exchange_rates(
        trades,
        exchange_rates,
        args.base_currency
    )

    if missing_exchange_rates:
        print_missing_exchange_rates(missing_exchange_rates)
        raise SystemExit

    calculator = Calculator(
        trades,
        exchange_rates,
        args.base_currency,
    )
    result = calculator.calculate(
        tax_year=args.tax_year,
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
        default=None,
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
        '--asset',
        default=DEFAULT_ASSET,
        help='The symbol of the crypto asset that was traded',
        type=str,
    )
    parser.add_argument(
        '--tax-year',
        default=None,
        help='The tax year to perform calculations for',
        type=int,
    )
    parser.add_argument(
        'trades',
        help='Path to CSV file(s) containing trade history',
        type=str,
        nargs='+',
    )
    return parser.parse_args()


def read_trade_files(filenames, asset):
    """
    Read the trade CSV files.
    """
    trades = []

    for filename in filenames:
        trades += read_trade_file(filename, asset)

    return trades


def read_trade_file(filename, target_asset):
    """
    Read the trades from a single CSV file.
    """
    csv_reader = CSVReader()
    return csv_reader.read_trades(filename, target_asset)


def read_exchange_rates(filename):
    """
    Read exchange rates from CSV.
    """
    exchange_rates = {}

    if filename:
        with open(filename, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if not row['date'] in exchange_rates:
                    exchange_rates[row['date']] = {}
                    exchange_rates[row['date']][row['currency']] = \
                        Decimal(row['rate'])

    return exchange_rates


def find_missing_exchange_rates(trades, exchange_rates, base_currency):
    """
    Validate exchange rates are present for all trade dates.
    """
    missing_dates = []

    for trade in trades:
        if trade['minor'] == base_currency:
            continue

        date_string = trade['dt'].strftime('%Y/%m/%d')

        if date_string not in exchange_rates or \
                trade['minor'] not in exchange_rates[date_string]:
            missing_dates.append({
                'date': date_string,
                'currency': trade['minor'],
            })

    return missing_dates


def print_missing_exchange_rates(missing_exchange_rates):
    """
    Print the dates for which exchange rates are missing.
    """
    print('The following exchange rates are missing:', file=stderr)

    for missing_exchange_rate in missing_exchange_rates:
        print(
            '{} {}'.format(
                missing_exchange_rate['date'],
                missing_exchange_rate['currency'],
            ),
            file=stderr
        )


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
