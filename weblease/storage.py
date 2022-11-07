from tortoise import Tortoise


async def init() -> None:
    await Tortoise.init(
        db_url="sqlite://tmp/db.sqlite3", modules={"models": ["weblease.models.models"]}
    )

    await Tortoise.generate_schemas()
