import logging
import typing as t
from io import StringIO

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def csv_to_dict(_in: str, rename: t.Optional[dict[str, str]] = None) -> list[dict[str, str]]:
    logger.info("Loading %d lines of CSV data into a dictionary", len(_in.splitlines()))

    def keep_cols(key: str) -> bool:
        return rename is None or key in rename

    df = (
        pd.read_csv(StringIO(_in), usecols=keep_cols, dtype=str)
        .replace({np.nan: None})
        .drop_duplicates()
    )

    if rename:
        df = df.rename(columns=rename)

    logger.info("The resulting DataFrame has %d rows x %d columns", *df.shape)
    logger.debug("DataFrame description\n%s", df.describe())

    return df.to_dict(orient="records")  # type: ignore[return-value]


def fwf_to_dict(_in: str, width_keys: list[tuple[str, int]]) -> list[dict[str, str]]:
    logger.info("Loading %d lines of fixed width data into a dictionary", len(_in.splitlines()))

    def keep_cols(key: str) -> bool:
        return not key.startswith("filler.")

    names, widths = zip(*width_keys)

    df = (
        pd.read_fwf(
            StringIO(_in),
            widths=widths,
            names=names,
            usecols=keep_cols,
            converters={n: str for n in names},
        )
        .replace({np.nan: None})
        .drop_duplicates()
    )

    logger.info("The resulting DataFrame has %d rows x %d columns", *df.shape)
    logger.debug("DataFrame description\n%s", df.describe())

    return df.to_dict(orient="records")  # type: ignore[return-value]
