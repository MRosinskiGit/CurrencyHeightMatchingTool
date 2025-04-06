import os.path
from pathlib import Path

import toml


def read_pyproject() -> dict:
    toml_file_path = os.path.join(Path(__file__).parent.parent, "pyproject.toml")
    with open(toml_file_path, "r", encoding="utf-8") as toml_file:
        return toml.load(toml_file)
