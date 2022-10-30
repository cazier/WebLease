import pathlib
import importlib
from unittest import mock

import httpx
from ward import test, raises

from tests.conftest import tmpdir
from weblease.loading import download


@test("download: from cache", tags=["download"])
def _(files_path: pathlib.Path = tmpdir) -> None:
    files_path.joinpath("cache_file.txt").write_text("cache file text")

    with mock.patch.dict(
        "os.environ", {"WEBLEASE_MOCK_DOWNLOAD": "1", "WEBLEASE_MOCK_DIRECTORY": str(files_path)}
    ):
        importlib.reload(download)

        response = download.get("https://example.com/cache_file.txt")
        assert response.read().decode(encoding="utf8") == "cache file text"

        with raises(httpx.HTTPStatusError):
            download.get("https://example.com/cache_file_missing.txt")
