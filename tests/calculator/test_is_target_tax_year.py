"""
Tests for the is target tax year function.
"""
from datetime import datetime

from crypto_taxes.calculator import is_target_tax_year


def test_is_target_tax_year_earlier_year():
    """
    Date in prior year is not considered target tax year.
    """
    prior_year = datetime(2017, 12, 31, 23, 59, 59)
    target_year = 2018
    assert not is_target_tax_year(prior_year, target_year)


def test_is_target_tax_year_future_year():
    """
    Date in future year is not considered target tax year.
    """
    future_year = datetime(2019, 1, 1, 0, 0, 0)
    target_year = 2018
    assert not is_target_tax_year(future_year, target_year)


def test_is_target_tax_year_with_target_year():
    """
    Date in target year is considered target tax year.
    """
    future_year = datetime(2018, 7, 1, 0, 0, 0)
    target_year = 2018
    assert is_target_tax_year(future_year, target_year)
