import pathlib
import tempfile

from ward import Scope, fixture


@fixture(scope=Scope.Global)
def tmpdir() -> pathlib.Path:
    with tempfile.TemporaryDirectory() as tempdir:
        path = pathlib.Path(tempdir)

        yield path
