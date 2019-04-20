"""
Custom exceptions.
"""


class InsufficientUnitsError(Exception):
    """
    Disposition of more units than held.
    """
    def __init__(self, trade_date, sold_units, units_held):
        self.trade_date = trade_date
        self.sold_units = sold_units
        self.units_held = units_held
        super(InsufficientUnitsError, self).__init__()

    def __str__(self):
        return 'Cannot sell {} units on {} when only holding {}'.format(
            self.sold_units,
            self.trade_date,
            self.units_held,
        )


class UnrecognizedFormatError(Exception):
    """
    The format of the CSV field could not be recognized.
    """
    def __init__(self, header):
        self.header = header
        super(UnrecognizedFormatError, self).__init__()
