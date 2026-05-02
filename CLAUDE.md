# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

An ESPHome external component (`bresser_weather`) that wraps the [BresserWeatherSensorReceiver](https://github.com/matthias-bs/BresserWeatherSensorReceiver) library to receive data from Bresser 5-in-1/6-in-1/7-in-1 868 MHz weather sensors via an ESP8266 or ESP32.

## Development Commands

Activate the Python environment first:
```bash
source venv/bin/activate
# or
conda activate esphome
```

All ESPHome commands run from the `test/` directory:
```bash
cd test/

esphome compile heltec_test.yaml        # compile only
esphome run heltec_test.yaml            # compile + upload + stream logs
esphome logs heltec_test.yaml           # stream logs from already-running device
esphome config heltec_test.yaml         # validate config and print resolved YAML
```

The `test/` directory is gitignored. YAML configs that live there (e.g. `test/heltec_test.yaml`) are not committed.

## Component Architecture

```
components/bresser_weather/
├── __init__.py          # ESPHome Python glue: config schema, build flags, lib deps
├── bresser_weather.h    # C++ class declaration
├── bresser_weather.cpp  # setup() / loop() implementation
├── WeatherSensorCfg.h   # Overrides the library's own WeatherSensorCfg.h (see below)
└── pre_build.py         # PlatformIO pre-build script registered via extra_scripts
```

### How the build override works

The library (`BresserWeatherSensorReceiver`) ships its own `WeatherSensorCfg.h` that selects the radio chip via board-specific `#ifdef ARDUINO_*` defines. Those board defines are **not** present when ESPHome compiles its own component sources (which are built as ESP-IDF components with generic `esp32s3` variant flags).

The fix (marius1 approach):
1. `__init__.py` emits `USE_SX1262` / `USE_CC1101` build flags and registers `pre_build.py` as a PlatformIO pre-build script using its absolute path.
2. `pre_build.py` (a SCons script) copies our `WeatherSensorCfg.h` into the downloaded library's `src/` dir, overriding the original. Our version maps `USE_SX1262` → `#define RADIO_CHIP SX1262`, etc.
3. `pre_build.py` also patches `WeatherSensor.cpp` in-place to thread a `PIN_RECEIVER_TCXO_MV` define through the `beginFSK()` call (needed for boards like Heltec v3 whose SX1262 is TCXO-only with no crystal).

**Important:** `__file__` is not available in SCons scripts. Use `env.get("PROJECT_SRC_DIR")` to find files in the ESPHome build tree, or `PROJECT_LIBDEPS_DIR` for library deps.

### Key `__init__.py` details

- `DEPENDENCIES = []` — intentionally empty so the component works on both ESP8266 and ESP32.
- Pin defaults are defined in the `DEFAULTS` dict per radio module; users can override in YAML.
- `tcxo_voltage` (float, volts) is converted to integer millivolts (`PIN_RECEIVER_TCXO_MV`) to avoid floating-point in C preprocessor defines.
- The SPI include path flag (`-I${platformio.packages_dir}/framework-arduinoespressif32/libraries/SPI/src`) is required because our `.cpp` includes `<SPI.h>` and is compiled as an ESP-IDF component, not an Arduino library.

### Heltec WiFi LoRa 32 V3 specifics

- Board: `heltec_wifi_lora_32_V3`, variant `esp32s3`
- SX1262 is **TCXO-only** (no crystal) — `tcxo_voltage: 1.8` is mandatory in the YAML
- Vext (GPIO36, active-low) powers the OLED and is driven LOW in `setup()` under `#if defined(USE_SX1262)`
- Logger needs `hardware_uart: UART0` to route output through the CP2102 USB-UART bridge (`/dev/cu.usbserial-*`)
- `ARDUINO_HELTEC_WIFI_LORA_32_V3` is **not** defined in any compilation unit in this build (neither component nor library code sees it; `ARDUINO_ESP32S3_DEV` is used instead)

### Battery sensor logic

`battery_ok` is published as `!battery_ok` from the library struct because Home Assistant's `BATTERY` device class uses inverted logic (ON = Low, OFF = OK).
