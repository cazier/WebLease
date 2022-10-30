# type: ignore

import pathlib
from io import BytesIO
from zipfile import ZipFile

from ward import Scope, test, raises, fixture

from tests.conftest import tmpdir
from weblease.loading.download import get, extract


@fixture(scope=Scope.Module)
def _setup_teardown(path: pathlib.Path = tmpdir) -> pathlib.Path:
    with ZipFile(path.joinpath("empty.zip"), mode="w") as _:
        pass

    with ZipFile(path.joinpath("not_empty.zip"), mode="w") as file:
        real_file = path.joinpath("textfile")
        real_file.write_text("text")
        file.write(real_file, real_file.relative_to(path))

    yield


@test("download: empty zip file", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = _setup_teardown) -> None:
    with raises(FileNotFoundError) as exception:
        extract(BytesIO(files_path.joinpath("empty.zip").read_bytes()))

    assert str(exception.raised) == "Unable to find a useful file in the archive"


@test("download: valid zip file", tags=["download"])
def _(files_path: pathlib.Path = tmpdir, _: None = _setup_teardown) -> None:
    assert extract(BytesIO(files_path.joinpath("not_empty.zip").read_bytes())) == "text"
