import os
import pathlib
import zipfile
import warnings
from io import BytesIO
from codecs import register_error, replace_errors

import httpx

if os.getenv("WEBLEASE_MOCK_DOWNLOAD") == "1":

    def handler(request: httpx.Request) -> httpx.Response:
        filename = request.url.path.split("/")[-1]

        if (file := pathlib.Path(cache_dir).joinpath(filename)).exists():
            return httpx.Response(200, content=file.read_bytes())

        return httpx.Response(404)

    cache_dir = os.getenv("WEBLEASE_MOCK_DIRECTORY", "cache")
    client = httpx.Client(transport=httpx.MockTransport(handler))

else:
    client = httpx.Client(transport=httpx.HTTPTransport())


def get(url: str) -> BytesIO:
    data = client.get(url, timeout=30)
    data.raise_for_status()

    return BytesIO(data.content)


def extract(zip_data: BytesIO) -> str:
    with zipfile.ZipFile(zip_data) as zip_file:
        for file in zip_file.filelist:
            if file.file_size > 0:
                return zip_file.read(file).decode("ascii", errors="replace_warning")

    raise FileNotFoundError("Unable to find a useful file in the archive")


def replace_warning(exception: UnicodeError) -> tuple[str | bytes, int]:
    warnings.warn('The loaded file had a malformed character string which was replaced by a "?"')
    return replace_errors(exception)


register_error("replace_warning", replace_warning)
