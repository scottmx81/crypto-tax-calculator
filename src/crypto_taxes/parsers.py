"""
Parsers for exchange CSV files.

The CSV export format is not consistent across all exchanges. These parsers
take a row from any given CSV, and return the relevant fields in a normalized
format.
"""
from datetime import datetime
from decimal import Decimal

from .exceptions import UnrecognizedFormatError


def get_parser(reader):
    """
    Gets the right parser for this CSV.
    """
    header = ','.join(reader.fieldnames)

    if header not in PARSER_MAP:
        raise UnrecognizedFormatError(header)

    return PARSER_MAP[header]()


class BitsoQCXParser():
    """
    Parser for Bitso & QuadrigaCX CSVs.
    """
    def parse_row(self, row):
        """
        Return CSV fields in normalized format.
        """
        return {
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


PARSER_MAP = {
    'type,major,minor,amount,rate,value,fee,total,timestamp,datetime':
        BitsoQCXParser
}
