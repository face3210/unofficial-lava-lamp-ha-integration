from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest

MODELS_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "lava_lamp"
    / "models.py"
)
SPEC = spec_from_file_location("lava_lamp_models", MODELS_PATH)
assert SPEC is not None
assert SPEC.loader is not None
models = module_from_spec(SPEC)
sys.modules[SPEC.name] = models
SPEC.loader.exec_module(models)
LavaLampState = models.LavaLampState


def test_state_parses_api_response() -> None:
    state = LavaLampState.from_api(
        {
            "rgb": [12, 34, 56],
            "hex": "#0c2238",
            "lastSetUnixMs": 1777951987215,
            "live": False,
        }
    )

    assert state.rgb == (12, 34, 56)
    assert state.red == 12
    assert state.green == 34
    assert state.blue == 56
    assert state.live is False


def test_state_rejects_invalid_rgb() -> None:
    with pytest.raises(ValueError):
        LavaLampState.from_api(
            {
                "rgb": [0, 0],
                "hex": "#000000",
                "lastSetUnixMs": 1777951987215,
                "live": True,
            }
        )
