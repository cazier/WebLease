import pathlib

from ward import Scope, fixture


@fixture(scope=Scope.Global)
def root() -> pathlib.Path:
    return pathlib.Path.cwd()


@fixture(scope=Scope.Global)
def files(root_path: pathlib.Path = root) -> pathlib.Path:
    return root_path.joinpath("tests", "files")
