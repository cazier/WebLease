import logging
import typing as t
from io import StringIO

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def csv_to_dict(_in: str, rename: dict[str, str]) -> list[dict[str, str]]:
    return csv_to_df(_in, rename).to_dict(orient="records")  # type: ignore[return-value]


def fwf_to_dict(_in: str, width_keys: list[tuple[str, int]]) -> list[dict[str, str]]:
    return fwf_to_df(_in, width_keys).to_dict(orient="records")  # type: ignore[return-value]


def csv_to_df(_in: str, rename: dict[str, str]) -> pd.DataFrame:
    logger.info("Loading %d lines of CSV data into a dictionary", len(_in.splitlines()))

    def keep_cols(key: str) -> bool:
        return key in rename

    df = (
        pd.read_csv(
            StringIO(_in),
            usecols=keep_cols,
            converters={n: _strip for n in rename.keys()},
        )
        .replace({np.nan: None})
        .drop_duplicates()
        .rename(columns=rename)
    )

    logger.info("The resulting DataFrame has %d rows x %d columns", *df.shape)
    logger.debug("DataFrame description\n%s", df.describe())

    return df


def fwf_to_df(_in: str, width_keys: list[tuple[str, int]]) -> pd.DataFrame:
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
            converters={n: _strip for n in names},
        )
        .replace({np.nan: None})
        .drop_duplicates()
    )

    logger.info("The resulting DataFrame has %d rows x %d columns", *df.shape)
    logger.debug("DataFrame description\n%s", df.describe())

    return df


def _strip(value: str) -> t.Optional[str]:
    """Helper function to clean values from input data. Strip away any whitespace from the front or
    end of the input string value. If the result is an empty string, return ``None``. Otherwise,
    return the string

    Args:
        value (str): the dirty input value

    Returns:
        t.Optional[str]: the cleaned/stripped value, or ``None``
    """
    value = str(value).strip()

    if value == "":
        return None

    return value
