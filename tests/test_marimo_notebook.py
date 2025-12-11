from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import marimo


def test_marimo_notebook_loads():
    notebook_path = (
        Path(__file__).resolve().parents[1] / "notebooks" / "combat_simulation.py"
    )
    assert notebook_path.exists(), "combat_simulation.py is missing"

    spec = spec_from_file_location("combat_simulation", notebook_path)
    assert spec and spec.loader

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "app")
    assert isinstance(module.app, marimo.App)
