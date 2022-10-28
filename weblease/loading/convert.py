import typing as t
from io import StringIO

import numpy as np
import pandas as pd


def csv_to_dict(_input: str, rename: t.Optional[dict[str, str]] = None) -> list[dict[str, str]]:
    df = pd.read_csv(StringIO(_input)).rename(columns=rename).replace({np.nan: None})

    return df.to_dict(orient="records")  # type: ignore[return-value]


def fwf_to_dict(_input: str, width_keys: list[tuple[str, int]]) -> list[dict[str, str]]:
    def keep_cols(key: str) -> bool:
        return not key.startswith("filler.")

    names, widths = zip(*width_keys)

    df = pd.read_fwf(StringIO(_input), widths=widths, names=names, usecols=keep_cols)

    return df.to_dict(orient="records")  # type: ignore[return-value]
