import datetime as dt
import typing as t

from tortoise import fields
from tortoise.models import Model

from weblease.models.utils import parse_date


class BseeDateField(fields.DateField):
    def to_python_value(self, value: t.Any) -> t.Optional[dt.date]:
        if value is not None and not isinstance(value, dt.date) and value != "":
            out = parse_date(value)

        else:
            out = None

        self.validate(out)
        return out

    def to_db_value(
        self, value: t.Optional[dt.date | str], instance: Model | t.Type[Model]
    ) -> t.Optional[dt.date]:
        if isinstance(value, str):
            return super().to_db_value(parse_date(value), instance)

        return super().to_db_value(value, instance)


class BaseCompany:
    number: str = fields.CharField(max_length=10)
    name: str = fields.CharField(max_length=100)
