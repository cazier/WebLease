# type: ignore

import typing as t
import pathlib

from ward import test

from weblease.loading.convert import csv_to_dict, fwf_to_dict

T = t.TypeVar("T")


def load(file: str, *nums: int):
    def get(_input: list[T], *nums: int) -> list[T]:
        return [e for i, e in enumerate(_input, start=1) if i in nums]

    if file not in ("csv", "fwf"):
        raise FileNotFoundError("Could not find an input file")

    out = pathlib.Path("tests", "files", f"input.{file}").read_text(encoding="utf8").splitlines()

    return "\n".join(get(out, 1, *nums))


@test("csv: generic load", tags=["csv"])
def _():
    data = load("csv", 2, 3)

    assert csv_to_dict(data) == [
        {"col1": "1", "col2": "2", "col3": "3", "col4": "4", "col5": "5"},
        {"col1": "one", "col2": "two", "col3": "three", "col4": "four", "col5": "five"},
    ]


@test("csv: remove duplicates", tags=["csv"])
def _():
    data = load("csv", 2, 3, 4)

    assert csv_to_dict(data) == [
        {"col1": "1", "col2": "2", "col3": "3", "col4": "4", "col5": "5"},
        {"col1": "one", "col2": "two", "col3": "three", "col4": "four", "col5": "five"},
    ]


@test("csv: rename columns", tags=["csv"])
def _():
    data = load("csv", 2, 3, 4)
    rename = {"col1": "col_a", "col2": "col_ii", "col3": "col333", "col4": "4col", "col5": "5"}

    assert csv_to_dict(data, rename=rename) == [
        {"col_a": "1", "col_ii": "2", "col333": "3", "4col": "4", "5": "5"},
        {"col_a": "one", "col_ii": "two", "col333": "three", "4col": "four", "5": "five"},
    ]


@test("csv: drop columns", tags=["csv"])
def _():
    data = load("csv", 2, 3, 4)
    rename = {"col1": "col1", "col3": "col3", "col4": "col4", "col5": "col5"}

    assert csv_to_dict(data, rename=rename) == [
        {"col1": "1", "col3": "3", "col4": "4", "col5": "5"},
        {"col1": "one", "col3": "three", "col4": "four", "col5": "five"},
    ]


@test("fwf: generic load", tags=["fwf"])
def _():
    data = load("fwf", 2, 3)
    width_keys = [("col1", 4), ("col2", 4), ("col3", 5), ("col4", 12), ("col5", 5)]

    assert fwf_to_dict(data, width_keys) == [
        {"col1": "1", "col2": "2", "col3": "3", "col4": "4", "col5": "5"},
        {"col1": "one", "col2": "two", "col3": "three", "col4": "four", "col5": "five"},
    ]


@test("fwf: remove duplicates", tags=["fwf"])
def _():
    data = load("fwf", 2, 3, 4)
    width_keys = [("col1", 4), ("col2", 4), ("col3", 5), ("col4", 12), ("col5", 5)]

    assert fwf_to_dict(data, width_keys) == [
        {"col1": "1", "col2": "2", "col3": "3", "col4": "4", "col5": "5"},
        {"col1": "one", "col2": "two", "col3": "three", "col4": "four", "col5": "five"},
    ]


@test("fwf: drop columns", tags=["fwf"])
def _():
    data = load("fwf", 2, 3, 4)
    width_keys = [("col1", 4), ("filler.1", 4), ("col3", 5), ("filler.2", 12), ("col5", 5)]

    assert fwf_to_dict(data, width_keys) == [
        {"col1": "1", "col3": "3", "col5": "5"},
        {"col1": "one", "col3": "three", "col5": "five"},
    ]
