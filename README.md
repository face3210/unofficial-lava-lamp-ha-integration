# Unofficial Lava Lamp Home Assistant Integration

Custom Home Assistant integration for the lava lamp RGB API.

The integration creates:

- `binary_sensor.lava_lamp_live`
- `sensor.lava_lamp_red`
- `sensor.lava_lamp_green`
- `sensor.lava_lamp_blue`
- `sensor.lava_lamp_hex`
- `sensor.lava_lamp_rgb_list`

## Install With HACS

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=face3210&repository=unofficial-lava-lamp-ha-integration&category=integration)

If the button does not work:

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/face3210/unofficial-lava-lamp-ha-integration`.
4. Select category `Integration`.
5. Install **Unofficial Lava Lamp** and restart Home Assistant.

## Setup

1. Go to **Settings** > **Devices & services**.
2. Select **Add Integration**.
3. Search for **Unofficial Lava Lamp**.
4. Enter the server URL. The default is `https://api.neurolavalamp.com`.
5. Optionally set an event delay in seconds to sync with your stream.

To change the server URL or delay later, open the integration options from
**Settings** > **Devices & services**.

## Recorder

The color entities can update quickly while the lamp is live. To avoid high
history churn, exclude them from recorder:

```yaml
recorder:
  exclude:
    entities:
      - sensor.lava_lamp_red
      - sensor.lava_lamp_green
      - sensor.lava_lamp_blue
      - sensor.lava_lamp_hex
      - sensor.lava_lamp_rgb_list
```

## Blueprint

This repository includes a light sync blueprint at
https://raw.githubusercontent.com/face3210/unofficial-lava-lamp-ha-integration/refs/heads/main/blueprints/automation/lava_lamp_rgb_light.yaml
Import the URL in Home Assistant from **Settings** >
**Automations & scenes** > **Blueprints** > **Import blueprint**.

The blueprint turns on a selected RGB light while `binary_sensor.lava_lamp_live`
is on and uses the list output as the light color:

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.example
    data:
      rgb_color: "{{ states('sensor.lava_lamp_rgb_list') | from_json }}"
```

## Manual Install

Copy `custom_components/lava_lamp` into your Home Assistant
`custom_components` directory, restart Home Assistant, then add the integration
from **Devices & services**.

## Repository Layout

```text
custom_components/lava_lamp/      Home Assistant custom integration
blueprints/automation/            Optional light sync blueprint
config/configuration.yaml         Local development Home Assistant config
scripts/                          Development helper commands
tests/                            Pytest test suite
```

## Development

This repository includes a development container modeled after
[`integration_blueprint`](https://github.com/ludeeus/integration_blueprint). It
installs Python 3.12, `uv`, Ruff, Home Assistant, and the VS Code extensions used
for local integration work.

From the development container:

```bash
scripts/setup
scripts/develop
```

`scripts/develop` starts a standalone Home Assistant instance with
`config/configuration.yaml` and loads `custom_components/lava_lamp` from this
repository by linking it into `config/custom_components/lava_lamp`.

If the local Home Assistant instance has stale onboarding entries or integrations
from earlier runs, reset the generated config files and start again:

```bash
scripts/reset-config
scripts/develop
```

If you are working outside the container, install
[`uv`](https://docs.astral.sh/uv/) and run:

```bash
uv sync --all-groups
uv run hass --config ./config --debug
```

## Linting And Tests

Ruff is used for both linting and formatting:

```bash
scripts/lint
uv run ruff check .
uv run ruff format . --check
```

Run the test suite with:

```bash
scripts/test
uv run pytest
```

## Validation

GitHub Actions runs:

- Ruff lint and format checks.
- Pytest.
- Home Assistant `hassfest` validation.
- HACS validation for the integration category.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, linting, testing, and issue
reporting guidance.
