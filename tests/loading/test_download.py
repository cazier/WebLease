# type: ignore

import pathlib
import warnings
from io import BytesIO
from zipfile import ZipFile

import httpx
import respx
from httpx import Response
from ward import Scope, fixture, raises, test

from tests.conftest import make_data, tmpdir
from weblease.loading.download import extract, fetch, get


@fixture(scope=Scope.Module)
def _setup_teardown(path: pathlib.Path = tmpdir, _: None = make_data) -> pathlib.Path:
    with ZipFile(path.joinpath("empty.zip"), mode="w") as _:
        pass

    with ZipFile(path.joinpath("not_empty.zip"), mode="w") as file:
        real_file = path.joinpath("textfile")
        real_file.write_text("text")
        file.write(real_file, real_file.relative_to(path))

    with ZipFile(path.joinpath("data.zip"), mode="w") as file:
        file.write(path.joinpath("input.csv"), real_file.relative_to(path))

    yield


@fixture(scope=Scope.Module)
def mocking(files_path: pathlib.Path = tmpdir):
    with respx.mock(base_url="https://example.com/") as mock:
        mock.get("empty.zip").mock(
            side_effect=httpx.HTTPStatusError("404 - Not Found", request=None, response=None)
        )

        file = mock.get("not_empty.zip")
        file.return_value = Response(200, content=files_path.joinpath("not_empty.zip").read_bytes())

        file = mock.get("data.zip")
        file.return_value = Response(200, content=files_path.joinpath("data.zip").read_bytes())

        yield


@test("extract: empty zip file", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = _setup_teardown) -> None:
    with raises(FileNotFoundError) as exception:
        extract(BytesIO(files_path.joinpath("empty.zip").read_bytes()))

    assert str(exception.raised) == "Unable to find a useful file in the archive"


@test("extract: valid zip file", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = _setup_teardown) -> None:
    assert extract(BytesIO(files_path.joinpath("not_empty.zip").read_bytes())) == "text"


@test("decode: warning on malformed character", tags=["download"])
def _() -> None:
    with warnings.catch_warnings(record=True) as warn:
        resp = chr(128).encode("utf8").decode("ascii", errors="replace_warning")

    assert "The loaded file had a malformed character string" in str(warn[-1].message)
    assert resp == "��"


@test("download: from remote 404", tags=["download"])
def _(_: respx.MockRouter = mocking) -> None:
    with raises(httpx.HTTPStatusError) as exception:
        get("https://example.com/empty.zip")

    assert str(exception.raised) == "404 - Not Found"


@test("download: from remote", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = mocking, __: None = _setup_teardown) -> None:
    response = get("https://example.com/not_empty.zip")

    assert files_path.joinpath("not_empty.zip").read_bytes() == response.read()


@test("fetch", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = mocking, __: None = _setup_teardown) -> None:
    data = fetch("https://example.com/data.zip")
    assert data == files_path.joinpath("input.csv").read_text()
