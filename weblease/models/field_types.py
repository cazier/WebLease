import datetime as dt
import typing as t

from tortoise import fields
from tortoise.models import Model

DATE_FORMATS = ("%m/%d/%Y", "%Y%m%d", "%Y-%m-%d")


class BseeDateField(fields.DateField):
    def to_python_value(self, value: t.Any) -> t.Optional[dt.date]:
        if value is not None and not isinstance(value, dt.date) and value != "":
            out = BseeDateField.parse_date(value)

        else:
            out = None

        self.validate(out)
        return out

    def to_db_value(
        self, value: t.Optional[dt.date | str], instance: Model | t.Type[Model]
    ) -> t.Optional[dt.date]:
        if isinstance(value, str):
            return super().to_db_value(BseeDateField.parse_date(value), instance)

        return super().to_db_value(value, instance)

    @staticmethod
    def parse_date(value: str) -> dt.date:
        for fmt in DATE_FORMATS:
            try:
                return dt.datetime.strptime(value, fmt).date()

            except ValueError:
                pass

        raise ValueError(f"Could not find parse a date value from: {value}")


class _Company:
    number: str = fields.CharField(max_length=10)
    name: str = fields.CharField(max_length=100)
