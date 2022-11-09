import datetime as dt

from tortoise import fields
from tortoise.models import Model

from weblease.models.enum_types import (
    FieldCode,
    LeaseSection,
    LeaseStatus,
    SerialType,
    SystemMeasureFlag,
    TerminationCode,
    WellTypes,
)
from weblease.models.field_types import BaseCompany, BseeDateField
from weblease.models.utils import FieldFinder


class Address(Model, FieldFinder):
    class Meta:
        table = "addresses"
        unique_together = ("address_one", "address_two", "city", "state", "zip_code", "country")

    __skip_annotations__: list[str] = ["__skip_annotations__", "companies"]

    address_one: str = fields.CharField(max_length=35, null=True)
    address_two: str = fields.CharField(max_length=35, null=True)
    city: str = fields.CharField(max_length=35, null=True)
    state: str = fields.CharField(max_length=2, null=True)
    zip_code: str = fields.CharField(max_length=20, null=True)
    country: str = fields.CharField(max_length=35, null=True)

    companies: fields.ManyToManyRelation["Company"] = fields.ManyToManyField(
        "models.Company", related_name="address"
    )


class Company(BaseCompany, Model):
    class Meta:
        table = "companies"

    start: dt.date = BseeDateField()
    # This max length is overridden to 100 in case the sort length is copied from the original name
    sort_name: str = fields.CharField(max_length=100, null=True)
    termination: dt.date = BseeDateField(null=True)
    region_pac: str = fields.CharField(max_length=1, null=True)  # Potential Enumeration
    region_gom: str = fields.CharField(max_length=1, null=True)  # Potential Enumeration
    region_alaska: str = fields.CharField(max_length=1, null=True)  # Potential Enumeration
    region_atl: str = fields.CharField(max_length=1, null=True)  # Potential Enumeration
    duns: str = fields.CharField(max_length=13, unique=True, null=True)
    termination_effective: dt.date = BseeDateField(null=True)
    termination_code: TerminationCode = fields.CharEnumField(
        TerminationCode, max_length=1, null=True
    )
    division_name: str = fields.CharField(max_length=13, null=True)

    def __init__(self, **kwargs: dict[str, str]) -> None:
        if kwargs.get("sort_name") is None:
            kwargs["sort_name"] = kwargs["name"]
        super().__init__(**kwargs)


class Lease(Model):
    class Meta:
        table = "leases"

    number: str = fields.CharField(max_length=20, unique=True)
    serial_type: SerialType = fields.CharEnumField(SerialType, max_length=1)
    sale: str = fields.CharField(max_length=7, null=True)
    expected_expiration: dt.date = BseeDateField(null=True)
    county: str = fields.CharField(max_length=5)
    tract: str = fields.CharField(max_length=10, null=True)
    effective: dt.date = BseeDateField(null=True)
    term: int = fields.IntField(null=True)
    expiration: dt.date = BseeDateField(null=True)
    bid_code: str = fields.CharField(max_length=5, null=True)  # Potential Enumeration
    royalty_rate: float = fields.FloatField(null=True)
    initial_area: float = fields.FloatField()
    current_area: float = fields.FloatField(null=True)
    rent_per_unit: float = fields.FloatField()
    bid_amount: float = fields.FloatField(null=True)
    bid_per_unit: float = fields.FloatField(null=True)
    low_depth: int = fields.IntField(null=True)
    max_depth: int = fields.IntField(null=True)
    measure_flag: SystemMeasureFlag = fields.CharEnumField(SystemMeasureFlag, max_length=1)
    planning_code: str = fields.CharField(max_length=3, null=True)  # Potential Enumeration
    district_code: int = fields.IntField()
    lease_status_code: LeaseStatus = fields.CharEnumField(LeaseStatus, max_length=6)
    lease_status_effective: dt.date = BseeDateField(null=True)
    suspension_expiration: dt.date = BseeDateField(null=True)
    # Potential Enumeration, but BSEE page has the length as one char, when the values can be two?
    suspension_type: str = fields.CharField(max_length=1, null=True)
    well_name: str = fields.CharField(max_length=6, null=True)
    well_type: WellTypes = fields.CharEnumField(WellTypes, max_length=1, null=True)
    lease_qualifying: dt.date = BseeDateField(null=True)
    discovery_type: str = fields.CharField(max_length=3, null=True)
    field_discover_code: FieldCode = fields.CharEnumField(FieldCode, max_length=1, null=True)
    distance_to_shore: str = fields.CharField(max_length=3, null=True)
    num_platforms: int = fields.IntField(null=True)
    platform_approval: dt.date = BseeDateField(null=True)
    first_platform_set: dt.date = BseeDateField(null=True)
    lease_section: LeaseSection = fields.CharEnumField(LeaseSection, max_length=2, null=True)
    postal_state: str = fields.CharField(max_length=4, null=True)
    lease_area: float = fields.FloatField(null=True)
    protraction: str = fields.CharField(max_length=7)
    suspension_effective: dt.date = BseeDateField(null=True)
    first_production: dt.date = BseeDateField(null=True)
    area_code: str = fields.CharField(max_length=2)  # Potential Enumeration
    block_number: str = fields.CharField(max_length=6)


class Block(Model):
    class Meta:
        table = "blocks"

    lease: fields.ForeignKeyRelation[Lease] = fields.ForeignKeyField(
        "models.Lease", related_name="leases"
    )

    area_code: str = fields.CharField(max_length=6)
    number: str = fields.CharField(max_length=18)
    status: LeaseStatus = fields.CharEnumField(LeaseStatus, max_length=6)
    effective: dt.date = BseeDateField(null=True)
    expiration: dt.date = BseeDateField(null=True)
    depth: int = fields.IntField()
