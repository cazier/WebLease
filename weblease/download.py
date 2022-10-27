import zipfile
from io import BytesIO

import requests


def get(url: str) -> BytesIO:
    data = requests.get(url, timeout=30)

    if not data.ok:
        raise requests.RequestException(f"Could not download the data from {url}")

    return BytesIO(data.content)


def extract(zip_data: BytesIO) -> str:
    with zipfile.ZipFile(zip_data) as zip_file:
        for file in zip_file.filelist:
            if file.file_size > 0:
                return zip_file.read(file).decode("ascii")

    raise FileNotFoundError("Unable to find a useful file in the archive")
