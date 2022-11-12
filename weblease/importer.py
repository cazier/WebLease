import datetime as dt
import logging
import pprint

from rich.progress import track
from tortoise import run_async
from tortoise.exceptions import MultipleObjectsReturned

from weblease import loading
from weblease.loading import csv_to_dict, fetch, fwf_to_dict
from weblease.models.models import Address, Block, Company, Lease, Owner
from weblease.models.utils import parse_date
from weblease.storage import init as init_db

logger = logging.getLogger(__name__)


async def load_leases() -> None:
    leases = fwf_to_dict(fetch(loading.LSETAPE_URL), loading.LSETAPE)

    for lease in track(leases):
        await Lease.get_or_create(defaults=None, using_db=None, **lease)


async def load_companies() -> None:
    companies = fwf_to_dict(fetch(loading.COMPALL_URL), loading.COMPALL)

    for company in track(companies):
        try:
            address, _ = await Address.get_or_create(
                defaults=None, using_db=None, **Address.pop_dict(company)
            )
            orm, _ = await Company.get_or_create(defaults=None, using_db=None, **company)
            await address.companies.add(orm)

        except ValueError:
            logger.info("Could not add the item to the database: \n%s", pprint.pformat(company))


async def load_blocks() -> None:
    blocks = csv_to_dict(fetch(loading.MV_LEASE_AREA_BLOCK_URL), loading.MV_LEASE_AREA_BLOCK_DICT)

    for block in track(blocks):
        lease = await Lease.get(number=block.pop("lease"))
        _, _ = await Block.get_or_create(defaults=None, using_db=None, **block, lease=lease)


async def load_owners() -> None:
    owners = csv_to_dict(fetch(loading.MV_LEASE_OWNERS_URL), loading.MV_LEASE_OWNERS_DICT)

    for owner in track(owners):
        lease = await Lease.get(number=owner.pop("lease"))

        keys = ("", "termination_effective", "termination")
        search: dict[str, str | dt.date | None] = {"number": owner.pop("number")}

        if start := owner.get("start"):
            search["start"] = parse_date(start)

        for key in keys:
            if key:
                search[key] = None

            try:
                company = await Company.get(defaults=None, using_db=None, **search)
                break

            except MultipleObjectsReturned:
                pass

        _, _ = await Owner.get_or_create(
            defaults=None, using_db=None, **owner, lease=lease, company=company
        )


async def main() -> None:
    await init_db()
    await load_leases()
    await load_blocks()
    await load_companies()
    await load_owners()


if __name__ == "__main__":
    run_async(main())
