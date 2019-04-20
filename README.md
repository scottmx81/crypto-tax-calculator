# Canadian Crypto Tax Calculator

A Python script for estimating the capital gains tax owed for crypto trades. It
reads in the CSV files provided by the exchanges, and reports the estimated
taxes owed, based on Canadian Adjusted Cost Base method used for Canadian
tax returns.

This script is for *estimation* only. Please contact your accountant for
official information on filing your return.

## Getting Started

### Installing

Set up virtualenv with:

`virtualenv -p python3 envname`

### Running the script:

Run the script with the command:

`python src/ctc.py --exchange-rates [EXCHANGE_RATE_CSV] [TRADE_CSVS]...`

### Supported Exchanges

This script currently supports CSV exports from QuadrigaCX & Bitso exchanges.

### Fiat Currencies & Exchange Rates

Trade values must be converted to the base currency for tax calculation
purposes. The default base currency is CAD, but this can be changed using
the `--base-currency` option, if there is another country using ACB method.

The script supports converting other fiat currencies to CAD for the tax
calculations. For example, if trades are made on Bitso in MXN currency,
the exchange rate file will be used to get the CAD value for each of those
trades.

The exchange rate CSV should have a header row, and have three columns:
* date (yyyy/mm/dd)
* currency (3 character code)
* rate (decimal)

For example:
`2018/01/01,mxn,15.57`

Use the `--exchange-rates` option to pass the path to the exchange rates CSV
file.

## License

This project is licensed under the MIT License - see the
[LICENSE.md](LICENSE.md) file for details.
