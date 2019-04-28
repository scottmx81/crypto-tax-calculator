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


def test_process_sell_all():
    """
    A sell performs the right calculations.

    Based on selling amounts purchased in the previous process buy first test.
    """
    trade = {
        'amount': Decimal('2'),
        'rate': Decimal('20'),
        'total': Decimal('39.8'),  # 0.5% commission: (2 * 40) * 0.995
        'value': Decimal('40'),  # Proceeds before commission: 2 * 40
    }

    tabulations = {
        'acb': Decimal('22'),
        'capital_gains': Decimal('0'),
        'proceeds': Decimal('0'),
        'sum_acb_dispositions': Decimal('0'),
        'units_held': Decimal('2'),
    }

    sut = Calculator()
    capital_gain = sut.process_sell(trade, tabulations)

    assert capital_gain == Decimal('17.8')
    assert Decimal('0') == tabulations['units_held']
    assert Decimal('0') == tabulations['acb']


def test_process_sell_partial():
    """
    A sell performs the right calculations, with units remaining after sale.
    """
    trade = {
        'amount': Decimal('50'),
        'rate': Decimal('120'),
        'total': Decimal('5990'),
        'value': Decimal('6000'),
    }

    tabulations = {
        'acb': Decimal('5010'),
        'capital_gains': Decimal('0'),
        'proceeds': Decimal('0'),
        'sum_acb_dispositions': Decimal('0'),
        'units_held': Decimal('100'),
    }

    sut = Calculator()
    capital_gain = sut.process_sell(trade, tabulations)

    assert capital_gain == Decimal('3485')
    assert Decimal('50') == tabulations['units_held']
    assert Decimal('2505') == tabulations['acb']
