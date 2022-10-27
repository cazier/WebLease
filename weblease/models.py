import typing as t
import datetime
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class BseeDateField(fields.DateField):
    def to_python_value(self, value: t.Any) -> t.Optional[datetime.date]:
        if value is not None and not isinstance(value, datetime.date) and value != "":
            out = datetime.datetime.strptime(value, "%m/%d/%Y").date()
        else:
            out = None

        self.validate(out)
        return out

    def to_db_value(
        self, value: t.Optional[datetime.date | str], instance: Model | t.Type[Model]
    ) -> t.Optional[datetime.date]:

        if value is not None and not isinstance(value, datetime.date):
            out = datetime.datetime.strptime(value, "%m/%d/%Y").date()
        else:
            out = None

        self.validate(out)
        return out


class Status(str, Enum):
    CURRENT = "C"
    HISTORIC = "H"
    PENDING = "P"
    TERMINATED = "T"


class Company(Model):
    leases: fields.ReverseRelation["Lease"]

    name: str = fields.TextField()
    mms_number: str = fields.CharField(max_length=10, unique=True)

    class Meta:
        table = "companies"


class Lease(Model):
    class Meta:
        table = "leases"

    lease_number: str = fields.CharField(max_length=20)
    aliquot: str = fields.CharField(max_length=1)
    status: Status = fields.CharEnumField(Status, max_length=1)
    start: datetime.date = BseeDateField(null=True)
    approved: datetime.date = BseeDateField()
    effective: datetime.date = BseeDateField()
    terminated: datetime.date = BseeDateField(null=True)
    group: str = fields.CharField(max_length=1, null=True)
    percentage: float = fields.FloatField(null=True)
    owner: str = fields.CharField(max_length=50)
    company: fields.ForeignKeyRelation[Company] = fields.ForeignKeyField(
        "models.Company", related_name="leases"
    )
