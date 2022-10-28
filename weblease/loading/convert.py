import typing as t
from io import StringIO

import numpy as np
import pandas as pd


def csv_to_dict(_input: str, header: t.Optional[list[str]] = None) -> list[dict[str, str]]:
    if header:
        df = pd.read_csv(StringIO(_input), header=None, names=header)

    else:
        df = pd.read_csv(StringIO(_input), header=0)

    return df.replace({np.nan: None}).to_dict(orient="records")  # type: ignore[return-value]


def fwf_to_dict(_input: str, width_keys: list[tuple[str, int]]) -> list[dict[str, str]]:
    def keep_cols(key: str) -> bool:
        return not key.startswith("filler.")

    names, widths = zip(*width_keys)

    return pd.read_fwf(StringIO(_input), widths=widths, names=names, usecols=keep_cols).to_dict(
        orient="records"
    )  # type: ignore[return-value]
