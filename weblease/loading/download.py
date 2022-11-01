import logging
import os
import pathlib
import warnings
import zipfile
from codecs import register_error, replace_errors
from io import BytesIO

import httpx

logger = logging.getLogger(__name__)

if os.getenv("WEBLEASE_MOCK_DOWNLOAD") == "1":
    logger.info("Configuring downloads to use local cache directory")

    def handler(request: httpx.Request) -> httpx.Response:
        filename = request.url.path.split("/")[-1]

        if (file := pathlib.Path(cache_dir).joinpath(filename)).exists():
            return httpx.Response(200, content=file.read_bytes())

        return httpx.Response(404)

    cache_dir = os.getenv("WEBLEASE_MOCK_DIRECTORY", "cache")
    client = httpx.Client(transport=httpx.MockTransport(handler))

else:
    logger.info("Configuring downloads to make actual network requests")
    client = httpx.Client(transport=httpx.HTTPTransport())


def get(url: str) -> BytesIO:
    logger.info("Downloading a file from: %s", url)

    data = client.get(url, timeout=30)
    data.raise_for_status()

    return BytesIO(data.content)


def extract(zip_data: BytesIO) -> str:
    with zipfile.ZipFile(zip_data) as zip_file:
        for file in zip_file.filelist:
            if file.file_size > 0:
                logger.info("Found a data file in the archive named: %s", file.filename)
                return zip_file.read(file).decode("ascii", errors="replace_warning")

    raise FileNotFoundError("Unable to find a useful file in the archive")


def fetch(url: str) -> str:
    return extract(get(url))


def replace_warning(exception: UnicodeError) -> tuple[str | bytes, int]:
    warnings.warn('The loaded file had a malformed character string which was replaced by a "?"')
    return replace_errors(exception)


register_error("replace_warning", replace_warning)
