"""
Tests for the exported CSV file formats from the exchanges.
"""
from datetime import datetime
from decimal import Decimal

from crypto_taxes import parsers


def test_parse_row():
    """
    The Bitso & QuadrigaCX parser returns a row in the normalized format.
    """
    sut = parsers.BitsoQCXParser()
    row = {
        'type': 'buy',
        'major': 'eth',
        'minor': 'mxn',
        'amount': '2.00000000',
        'rate': '6815.00',
        'value': '13630.00000000',
        'fee': '0.02000000',
        'total': '1.98000000',
        'timestamp': '1522889881.138',
        'datetime': '04/04/2018 19:58:01',
    }
    expected = {
        'type': 'buy',
        'major': 'eth',
        'minor': 'mxn',
        'amount': Decimal('2.00000000'),
        'rate': Decimal('6815.00'),
        'value': Decimal('13630.00000000'),
        'total': Decimal('1.98000000'),
        'dt': datetime(2018, 4, 4, 19, 58, 1, 138000),
        'timestamp': float('1522889881.138')
    }
    assert expected == sut.parse_row(row)
