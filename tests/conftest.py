import pathlib
import tempfile

from ward import Scope, fixture


@fixture(scope=Scope.Global)
def tmpdir() -> pathlib.Path:
    with tempfile.TemporaryDirectory() as tempdir:
        path = pathlib.Path(tempdir)

        yield path


@fixture(scope=Scope.Module)
def make_data(path: pathlib.Path = tmpdir) -> pathlib.Path:
    path.joinpath("input.csv").write_text(
        """col1,col2,col3,col4,col5
1,2,3,4,5
"one","two","three","four","five"
"one","two","three","four","five"
"""
    )

    path.joinpath("input.fwf").write_text(
        """   1   2    3           4    5
one two three        four five
one two three        four five
"""
    )

    yield
