# CHMI Weather Home Assistant Integration

A custom integration for [Home Assistant](https://www.home-assistant.io/) that fetches and displays current weather data from the Czech Hydrometeorological Institute's (CHMI/ČHMÚ) public open data feed.

## Features

- Fetches up-to-date weather measurements from CHMI.
- Supports multiple weather elements including:
  - Temperature (current, max, min, ground)
  - Wind speed (current, max, average)
  - Wind direction
  - Rainfall (10-minute sum)
  - Solar radiation
  - Humidity
  - Pressure
- Automatically selects the most recent measurement per element.
- Displays units and timestamps as extra attributes.
- Configurable via the Home Assistant UI.

## Installation

1. Copy the `custom_components/chmi_weather/` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**.
4. Search for `CHMI Weather` and select it.
5. Choose a weather station location from the list.

## Configuration

No YAML configuration is needed. All setup is handled via the UI.

## Attribution & Disclaimer

This integration uses public data from the [Czech Hydrometeorological Institute (CHMI)](https://www.chmi.cz/) available through their [Open Data portal](https://opendata.chmi.cz/).

**Disclaimer:** This project is not developed by or affiliated with the Czech Hydrometeorological Institute. Use at your own risk.