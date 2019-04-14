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

`python crypto_taxes/crypto_taxes.sh --exchange-rates [EXCHANGE_RATE_CSV] [TRADE_CSVS]...`

## License

This project is licensed under the MIT License - see the
[LICENSE.md](LICENSE.md) file for details.
