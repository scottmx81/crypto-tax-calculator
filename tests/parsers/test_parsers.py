"""
Tests for the exported CSV file formats from the exchanges.
"""
from csv import DictReader
from datetime import datetime
from decimal import Decimal
from io import StringIO

import pytest

from crypto_taxes import parsers
from crypto_taxes.exceptions import UnrecognizedFormatError


def test_get_parser_header_matches():
    """
    Get parser returns a parser class when the header matches one in the map.
    """
    csvfile = StringIO(
        'type,major,minor,amount,rate,value,fee,total,timestamp,datetime\n'
    )
    reader = DictReader(csvfile)
    parser = parsers.get_parser(reader)
    assert parser.__class__ == parsers.BitsoQCXParser


def test_get_parser_header_unrecognized():
    """
    Get parser raises unrecognized format error when header is not recognized.
    """
    csvfile = StringIO(
        'unrecognized,fields\n'
    )
    reader = DictReader(csvfile)

    with pytest.raises(UnrecognizedFormatError):
        parsers.get_parser(reader)


def test_bitso_qcx_parse_row():
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
