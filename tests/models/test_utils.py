import datetime

from ward import raises, test

from weblease.models.utils import parse_date


@test("parse_date: good", tags=["models"])
def _() -> None:
    for date in ["10/01/2011", "20111001", "2011-10-01"]:
        assert parse_date(date) == datetime.date(2011, 10, 1)


@test("parse_date: none", tags=["models"])
def _() -> None:
    assert parse_date(None) is None


@test("parse_date: bad", tags=["models"])
def _() -> None:
    for date in ["10012011", "00000000", "date", False, "", []]:
        with raises(ValueError) as exception:
            parse_date(date)

        assert "Could not parse a date value from: " in str(exception.raised)

    with raises(TypeError) as exception:
        parse_date()  # pylint: disable=no-value-for-parameter

    assert "parse_date() missing 1 required positional argument: 'value'" == str(exception.raised)
