import logging
import pprint

from rich.progress import track
from tortoise import run_async

from weblease.loading import fetch
from weblease.models.models import Address, Company, Lease
from weblease.storage import init as init_db

logger = logging.getLogger(__name__)


async def load_leases() -> None:
    leases = Lease.Meta.method(fetch(Lease.Meta.url), Lease.Meta.util)

    for lease in track(leases):
        await Lease.get_or_create(**lease)


async def load_companies() -> None:
    companies = Company.Meta.method(fetch(Company.Meta.url), Company.Meta.util)

    for company in track(companies):
        try:
            address, _ = await Address.get_or_create(**Address.pop_dict(company))
            company, _ = await Company.get_or_create(**company)
            await address.companies.add(company)

        except ValueError:
            logger.info("Could not add the item to the database: \n%s", pprint.pformat(company))


async def main() -> None:
    await init_db()
    await load_leases()
    await load_companies()


if __name__ == "__main__":
    run_async(main())
