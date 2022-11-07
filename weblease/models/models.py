import datetime as dt
import typing as t
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class BseeDateField(fields.DateField):
    def to_python_value(self, value: t.Any) -> t.Optional[dt.date]:
        if value is not None and not isinstance(value, dt.date) and value != "":
            try:
                out = dt.datetime.strptime(value, "%m/%d/%Y").date()
            except ValueError:
                try:
                    out = dt.datetime.strptime(value, "%Y%m%d").date()
                except ValueError as exception:
                    raise exception

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
        try:
            return dt.datetime.strptime(value, "%m/%d/%Y").date()

        except ValueError:
            try:
                return dt.datetime.strptime(value, "%Y%m%d").date()

            except ValueError as exception:
                raise exception


class _Company:

    # leases: fields.ReverseRelation["Lease"]

    number: str = fields.CharField(max_length=10)
    name: str = fields.TextField()


class Company(_Company, Model):
    class Meta:
        table = "companies"

    class TerminationCode(str, Enum):
        CHANGE_OF_NAME = "C"
        MERGER = "M"
        OTHER = "O"

    start: dt.date = BseeDateField()
    sort_name: str = fields.CharField(max_length=75, null=True)
    termination: dt.date = BseeDateField(null=True)
    region_pac: str = fields.CharField(max_length=1, null=True)
    region_gom: str = fields.CharField(max_length=1, null=True)
    region_alaska: str = fields.CharField(max_length=1, null=True)
    region_atl: str = fields.CharField(max_length=1, null=True)
    duns: str = fields.CharField(max_length=13, unique=True, null=True)
    termination_effective: dt.date = BseeDateField(null=True)
    termination_code: TerminationCode = fields.CharEnumField(
        TerminationCode, max_length=1, null=True
    )
    division_name: str = fields.CharField(max_length=13, null=True)
    address_one: str = fields.CharField(max_length=35, null=True)
    address_two: str = fields.CharField(max_length=35, null=True)
    city: str = fields.CharField(max_length=35, null=True)
    state: str = fields.CharField(max_length=2, null=True)
    zip_code: str = fields.CharField(max_length=20, null=True)
    country: str = fields.CharField(max_length=35, null=True)


# class Operator(_Company):
#     class Meta:
#         table = "operators"


# class Lease(Model):
#     class Meta:
#         table = "leases"

#     class Status(str, Enum):
#         CURRENT = "C"
#         HISTORIC = "H"
#         PENDING = "P"
#         TERMINATED = "T"

#     blocks: fields.ReverseRelation["Block"]

#     lease_number: str = fields.CharField(max_length=20)
#     aliquot: str = fields.CharField(max_length=1)
#     status: Status = fields.CharEnumField(Status, max_length=1)
#     start: dt.date = BseeDateField(null=True)
#     approved: dt.date = BseeDateField()
#     effective: dt.date = BseeDateField()
#     terminated: dt.date = BseeDateField(null=True)
#     group: str = fields.CharField(max_length=1, null=True)
#     percentage: float = fields.FloatField(null=True)
#     owner: str = fields.CharField(max_length=50)
#     company: fields.ForeignKeyRelation[Company] = fields.ForeignKeyField(
#         "models.Company", related_name="leases"
#     )
#     operator: fields.ForeignKeyRelation[Operator] = fields.ForeignKeyField(
#         "models.Operator", related_name="leases"
#     )


class Block(Model):
    class Meta:
        table = "blocks"

    class Status(str, Enum):
        CANCEL = "CANCEL"
        CONSOL = "CONSOL"
        DSO = "DSO"
        EXPIR = "EXPIR"
        NO_EXE = "NO-EXE"
        NO_ISS = "NO-ISS"
        OPERNS = "OPERNS"
        PRIMRY = "PRIMRY"
        PROD = "PROD"
        REJECT = "REJECT"
        RELINQ = "RELINQ"
        SOO = "SOO"
        SOP = "SOP"
        TERMIN = "TERMIN"
        UNIT = "UNIT"

    lease: str = fields.CharField(max_length=6)
    block: str = fields.TextField()
    area_code: str = fields.CharField(max_length=6)
    # https://www.data.boem.gov/Leasing/LeaseAreaBlock/FieldValues.aspx?domain=0059
    effective: dt.date = BseeDateField(null=True)
    expiration: dt.date = BseeDateField(null=True)
    depth: int = fields.IntField()
    status: Status = fields.CharEnumField(Status, max_length=10)
    # https://www.data.boem.gov/Leasing/LeaseAreaBlock/FieldValues.aspx?domain=LEASE_STATUS_CDS
    # lease: fields.ForeignKeyRelation[Lease] = fields.ForeignKeyField(
    #     "models.Lease", related_name="blocks"
    # )
