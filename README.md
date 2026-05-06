# Unofficial Lava Lamp Home Assistant Integration

Custom Home Assistant integration for the lava lamp RGB API.

The integration creates:

- `binary_sensor.lava_lamp_live`
- `sensor.lava_lamp_red`
- `sensor.lava_lamp_green`
- `sensor.lava_lamp_blue`

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
4. Enter the server URL. The default is `http://45.61.59.181:8080`.

## Manual Install

Copy `custom_components/lava_lamp` into your Home Assistant
`custom_components` directory, restart Home Assistant, then add the integration
from **Devices & services**.
