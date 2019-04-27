from decimal import Decimal

from crypto_taxes.calculator import Calculator


def test_process_buy_first():
    """
    A buy when it's the first trade, with no acb or units held yet.

    ACB = (2 * 10) + (0.2 * 10) = 20 + 2 = 22
    """
    trade = {
        'amount': Decimal('2.2'),
        'rate': Decimal('10'),
        'total': Decimal('2'),
    }

    tabulations = {
        'acb': Decimal('0'),
        'units_held': Decimal('0'),
        'outlays': Decimal('0'),
    }

    sut = Calculator()
    capital_gain = sut.process_buy(trade, tabulations)

    assert capital_gain == 0
    assert Decimal('22') == tabulations['acb']
