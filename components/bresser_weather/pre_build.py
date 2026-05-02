import os
import re
import shutil
from SCons.Script import Import

Import("env")

component_dir = os.path.join(env.get("PROJECT_SRC_DIR"), "esphome", "components", "bresser_weather")
libdeps_dir = os.path.join(env.get("PROJECT_LIBDEPS_DIR"), env.get("PIOENV"), "BresserWeatherSensorReceiver", "src")


def copy_cfg():
    src = os.path.join(component_dir, "WeatherSensorCfg.h")
    dest = os.path.join(libdeps_dir, "WeatherSensorCfg.h")
    if not os.path.exists(src):
        raise FileNotFoundError(f"BRESSER WEATHER: WeatherSensorCfg.h not found at: {src}")
    print(f"BRESSER WEATHER: Overriding WeatherSensorCfg.h in: {dest}")
    shutil.copy(src, dest)


def patch_tcxo():
    ws_path = os.path.join(libdeps_dir, "WeatherSensor.cpp")
    if not os.path.exists(ws_path):
        print(f"BRESSER WEATHER: WeatherSensor.cpp not found at {ws_path}, skipping TCXO patch")
        return

    with open(ws_path, "r") as f:
        content = f.read()

    # Already patched
    if "PIN_RECEIVER_TCXO_MV" in content:
        print("BRESSER WEATHER: WeatherSensor.cpp TCXO patch already applied")
        return

    old = "    int state = radio.beginFSK(frequency, 8.21, 57.136417, 234.3, 10, 32);"
    new = (
        "#if defined(PIN_RECEIVER_TCXO_MV)\n"
        "    int state = radio.beginFSK(frequency, 8.21, 57.136417, 234.3, 10, 32, (float)(PIN_RECEIVER_TCXO_MV) / 1000.0f);\n"
        "#else\n"
        "    int state = radio.beginFSK(frequency, 8.21, 57.136417, 234.3, 10, 32);\n"
        "#endif"
    )

    if old not in content:
        print("BRESSER WEATHER: WeatherSensor.cpp TCXO patch target not found — version mismatch?")
        return

    patched = content.replace(old, new, 1)
    with open(ws_path, "w") as f:
        f.write(patched)
    print("BRESSER WEATHER: Patched WeatherSensor.cpp with TCXO support")


copy_cfg()
patch_tcxo()


def middleware(node):
    if "BresserWeatherSensorReceiver" in node.get_path():
        env.AppendUnique(CPPDEFINES=[("FORCE_REBUILD", 1)])
    return node


env.AddBuildMiddleware(middleware)
