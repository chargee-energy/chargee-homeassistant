# Chargee P1 for Home Assistant

[![Validate](https://github.com/chargee-energy/chargee-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/chargee-energy/chargee-homeassistant/actions/workflows/validate.yml)
[![Tests](https://github.com/chargee-energy/chargee-homeassistant/actions/workflows/tests.yml/badge.svg)](https://github.com/chargee-energy/chargee-homeassistant/actions/workflows/tests.yml)
[![hacs](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)

A custom [Home Assistant](https://www.home-assistant.io/) integration for the
**Chargee P1 dongle** (**Sparky** and **Flint**). It reads your smart meter data
directly from the dongle over its **Local API** and feeds it straight into the
Home Assistant **Energy dashboard** - no cloud account required.

The integration is built from scratch, taking inspiration from the HomeWizard
Energy integration's structure and UX, but implemented specifically for the
Chargee Local API.

> **Note:** A future release will optionally support connecting through the
> Chargee Web API. That option is not available yet; today the integration
> talks to your device **locally only**. See [Roadmap](#roadmap).

---

## Features

- Automatic discovery of Sparky and Flint devices on your network via **mDNS**.
- 100% local polling - your data never leaves your network.
- Full mapping to the **Home Assistant Energy dashboard** (grid import, grid
  export, and gas).
- Per-phase power, voltage and current sensors for three-phase meters.
- Tariff, Wi-Fi and meter diagnostics.
- An **Identify** button that blinks the device status light.
- Diagnostics download support for troubleshooting.

## Supported devices

| Device | Minimum firmware | Notes |
| ------ | ---------------- | ----- |
| Sparky | 95               | Local API enabled by default from this version |
| Flint  | 105              | Local API enabled by default from this version |

The integration uses **Local API v1** (`api_version: "v1"`), served over HTTP on
port 80, and advertised on the network as the `_chargee_p1._tcp` mDNS service.

---

## Before you start: enable the Local API

The Local API is enabled by default on supported firmware, but you can verify it
in the Chargee app:

1. Open the **Chargee app**.
2. Go to **Profile -> your Address -> My House -> Local API**.
3. Make sure the Local API is enabled.

> Optional: enabling **"Previous P1 meters"** turns on *compatibility mode*,
> which additionally broadcasts the legacy P1 service on port 3602. This
> integration does **not** require compatibility mode - it uses the modern
> Local API v1.

---

## Installation

### HACS (recommended)

1. In Home Assistant, go to **HACS -> Integrations**.
2. Open the overflow menu (top right) and choose **Custom repositories**.
3. Add `https://github.com/chargee-energy/chargee-homeassistant` with category
   **Integration**.
4. Search for **Chargee P1** and install it.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/chargee` folder into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Setup

### Automatic discovery

Once your Sparky or Flint is online, Home Assistant will discover it
automatically. You'll see a **"Discovered"** card under
**Settings -> Devices & Services**. Click **Configure** and confirm.

### Manual setup

If discovery doesn't find your device (e.g. mDNS is blocked between VLANs):

1. Go to **Settings -> Devices & Services -> Add Integration**.
2. Search for **Chargee P1**.
3. Enter the **IP address** of your dongle (and port, if not 80).

The integration validates the connection by calling `/api` and uses the device
**serial number** as its unique identifier, so a device is never added twice.

---

## Entities

Entities are created only for the data points your meter actually reports, so a
single-phase Flint without gas will expose fewer entities than a three-phase
Sparky with gas. Some less-common sensors are disabled by default; enable them
from the entity settings if you need them.

### Energy (for the Energy dashboard)

| Entity | Unit | Device class | State class | Enabled by default |
| ------ | ---- | ------------ | ----------- | ------------------ |
| Energy import | kWh | energy | total_increasing | Yes |
| Energy import tariff 1 | kWh | energy | total_increasing | No |
| Energy import tariff 2 | kWh | energy | total_increasing | No |
| Energy export | kWh | energy | total_increasing | Yes |
| Energy export tariff 1 | kWh | energy | total_increasing | No |
| Energy export tariff 2 | kWh | energy | total_increasing | No |
| Gas | m3 | gas | total_increasing | Yes |

### Power, voltage and current

| Entity | Unit | Device class | Enabled by default |
| ------ | ---- | ------------ | ------------------ |
| Active power | W | power | Yes |
| Active power phase 1/2/3 | W | power | Yes |
| Voltage phase 1/2/3 | V | voltage | No |
| Current | A | current | Yes |
| Current phase 1/2/3 | A | current | No |

### Diagnostics

| Entity | Description |
| ------ | ----------- |
| Active tariff | Current tariff (1 or 2) |
| Wi-Fi strength | Signal strength in % |
| Wi-Fi SSID | Network the dongle is connected to |
| Smart meter model | Brand/model reported by the meter |
| DSMR version | Smart meter DSMR/SMR version |
| Gas timestamp | Timestamp of the most recent gas reading |

### Controls

| Entity | Description |
| ------ | ----------- |
| Identify (button) | Blinks the status light green for 5 seconds |

---

## Configuring the Energy dashboard

1. Go to **Settings -> Dashboards -> Energy**.
2. Under **Electricity grid**:
   - **Grid consumption** -> select **Energy import**.
   - **Return to grid** -> select **Energy export**.
   - (Optional) Add your energy tariffs / costs.
3. Under **Gas consumption** (if your meter reports gas) -> select **Gas**.
4. Save. Home Assistant starts building long-term statistics on the next cycle.

> If you want tariff-split statistics, enable the **tariff 1/2** import and
> export sensors first, then add them instead of the combined sensors.

---

## How it works

```
mDNS (_chargee_p1._tcp)            HTTP (port 80)
        |                                 |
        v                                 v
  Config flow  ->  Config entry  ->  Coordinator  ->  Local API client
                                          |                  |
                                          v                  v
                                    Sensors / Button    /api, /api/v1/data,
                                                        /api/v1/telegram,
                                                        /api/v1/identify
```

The integration polls `/api/v1/data` every few seconds through a
`DataUpdateCoordinator`, and reads static device information from `/api` once.
The bundled async API client lives in
[`custom_components/chargee/api/`](custom_components/chargee/api) and has no
Home Assistant dependencies, so it can be unit-tested in isolation and reused
later for the Web API.

---

## Troubleshooting

- **Device not discovered:** Ensure the dongle and Home Assistant are on the
  same network/VLAN and that mDNS (UDP 5353) is allowed. Use **manual setup**
  with the device IP as a fallback.
- **Cannot connect:** Confirm the Local API is enabled in the Chargee app and
  that you can reach `http://<device-ip>/api` from a browser or with
  `curl http://<device-ip>/api`.
- **Some sensors are missing:** This is expected - the API only sends data
  points your meter actually provides. Single-phase meters won't have L2/L3
  sensors, and meters without gas won't have a gas sensor.
- **Statistics not showing in Energy dashboard:** Long-term statistics are
  generated on a schedule; allow up to an hour after adding the sensors.

### Diagnostics

For bug reports, download diagnostics from the device page
(**Settings -> Devices & Services -> Chargee P1 -> Download diagnostics**).
Sensitive values (host, serial, gas/meter IDs, Wi-Fi SSID) are redacted.

---

## Local API reference

The integration uses the following endpoints (Local API v1):

| Endpoint | Method | Description |
| -------- | ------ | ----------- |
| `/api` | GET | Device info: `product_type`, `product_name`, `serial`, `firmware_version`, `api_version` |
| `/api/v1/data` | GET | Most recent measurement (JSON, optional fields) |
| `/api/v1/telegram` | GET | Most recent raw, validated DSMR telegram (text) |
| `/api/v1/identify` | GET | Blinks the status light |

---

## Roadmap

- [ ] **Web API connection** - connect to your device through the Chargee Web
      API for access outside your local network. The client layer is already
      structured so a cloud client can return the same data models, but the Web
      API is not publicly available yet.
- [ ] Expose the raw DSMR telegram as a service/diagnostic.
- [ ] Additional translations.

---

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
```

The test suite uses
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
and mocks all network traffic; no device is required.

## License

[MIT](LICENSE)

> Chargee, Sparky and Flint are trademarks of their respective owner. This is a
> community integration.
