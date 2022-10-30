import typing as t
from io import StringIO

import numpy as np
import pandas as pd


def csv_to_dict(_input: str, rename: t.Optional[dict[str, str]] = None) -> list[dict[str, str]]:
    def keep_cols(key: str) -> bool:
        return rename is None or key in rename

    df = pd.read_csv(StringIO(_input), usecols=keep_cols).replace({np.nan: None})

    if rename:
        df = df.rename(columns=rename)

    return df.drop_duplicates().to_dict(orient="records")  # type: ignore[return-value]


def fwf_to_dict(_input: str, width_keys: list[tuple[str, int]]) -> list[dict[str, str]]:
    def keep_cols(key: str) -> bool:
        return not key.startswith("filler.")

    names, widths = zip(*width_keys)

    df = pd.read_fwf(StringIO(_input), widths=widths, names=names, usecols=keep_cols)

    return df.drop_duplicates().to_dict(orient="records")  # type: ignore[return-value]
