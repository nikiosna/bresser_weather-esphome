import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, binary_sensor, text_sensor
from esphome.const import (
    CONF_ID,
    CONF_TEMPERATURE,
    CONF_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    UNIT_CELSIUS,
    UNIT_PERCENT,
)

DEPENDENCIES = []
AUTO_LOAD = ["sensor", "binary_sensor", "text_sensor"]

CONF_RADIO_MODULE = "radio_module"
CONF_CS_PIN = "cs_pin"
CONF_IRQ_PIN = "irq_pin"
CONF_RST_PIN = "rst_pin"
CONF_BUSY_PIN = "busy_pin"
CONF_SPI_CLK_PIN = "spi_clk_pin"
CONF_SPI_MOSI_PIN = "spi_mosi_pin"
CONF_SPI_MISO_PIN = "spi_miso_pin"

CONF_WIND_GUST = "wind_gust"
CONF_WIND_SPEED = "wind_speed"
CONF_WIND_DIRECTION = "wind_direction"
CONF_RAIN = "rain"
CONF_UV = "uv"
CONF_LIGHT = "light"
CONF_RSSI = "rssi"
CONF_BATTERY_OK = "battery_ok"
CONF_SENSOR_ID = "sensor_id"
CONF_FILTER_SENSOR_ID = "filter_sensor_id"

# Custom units not in const
UNIT_METER_PER_SECOND = "m/s"
UNIT_MILLIMETER = "mm"
UNIT_DEGREES = "°"
UNIT_KILOLUX = "klx"
UNIT_DBM = "dBm"

RADIO_MODULE_CC1101 = "cc1101"
RADIO_MODULE_SX1262 = "sx1262"

# Default pins per radio module
DEFAULTS = {
    RADIO_MODULE_CC1101: {
        CONF_CS_PIN: 15,
        CONF_IRQ_PIN: 4,
        CONF_RST_PIN: -1,   # RADIOLIB_NC
        CONF_BUSY_PIN: -1,  # not used
        CONF_SPI_CLK_PIN: -1,
        CONF_SPI_MOSI_PIN: -1,
        CONF_SPI_MISO_PIN: -1,
    },
    RADIO_MODULE_SX1262: {
        CONF_CS_PIN: 8,
        CONF_IRQ_PIN: 14,   # DIO1
        CONF_RST_PIN: 12,
        CONF_BUSY_PIN: 13,
        CONF_SPI_CLK_PIN: 9,
        CONF_SPI_MOSI_PIN: 10,
        CONF_SPI_MISO_PIN: 11,
    },
}

bresser_weather_ns = cg.esphome_ns.namespace("bresser_weather")
BresserWeatherComponent = bresser_weather_ns.class_("BresserWeatherComponent", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(BresserWeatherComponent),
        cv.Optional(CONF_RADIO_MODULE, default=RADIO_MODULE_CC1101): cv.one_of(
            RADIO_MODULE_CC1101, RADIO_MODULE_SX1262, lower=True
        ),
        cv.Optional(CONF_CS_PIN): cv.int_,
        cv.Optional(CONF_IRQ_PIN): cv.int_,
        cv.Optional(CONF_RST_PIN): cv.int_,
        cv.Optional(CONF_BUSY_PIN): cv.int_,
        cv.Optional(CONF_SPI_CLK_PIN): cv.int_,
        cv.Optional(CONF_SPI_MOSI_PIN): cv.int_,
        cv.Optional(CONF_SPI_MISO_PIN): cv.int_,
        cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
            unit_of_measurement=UNIT_CELSIUS,
            accuracy_decimals=1,
            device_class=DEVICE_CLASS_TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_HUMIDITY): sensor.sensor_schema(
            unit_of_measurement=UNIT_PERCENT,
            accuracy_decimals=0,
            device_class=DEVICE_CLASS_HUMIDITY,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_WIND_GUST): sensor.sensor_schema(
            unit_of_measurement=UNIT_METER_PER_SECOND,
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_WIND_SPEED): sensor.sensor_schema(
            unit_of_measurement=UNIT_METER_PER_SECOND,
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_WIND_DIRECTION): sensor.sensor_schema(
            unit_of_measurement=UNIT_DEGREES,
            accuracy_decimals=0,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_RAIN): sensor.sensor_schema(
            unit_of_measurement=UNIT_MILLIMETER,
            accuracy_decimals=1,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
        cv.Optional(CONF_UV): sensor.sensor_schema(
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_LIGHT): sensor.sensor_schema(
            unit_of_measurement=UNIT_KILOLUX,
            accuracy_decimals=1,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_RSSI): sensor.sensor_schema(
            unit_of_measurement=UNIT_DBM,
            accuracy_decimals=1,
            device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        cv.Optional(CONF_BATTERY_OK): binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_BATTERY,
        ),
        cv.Optional(CONF_SENSOR_ID): text_sensor.text_sensor_schema(),
        cv.Optional(CONF_FILTER_SENSOR_ID): cv.hex_uint32_t,
    }
).extend(cv.COMPONENT_SCHEMA)


def _pin(config, key, module):
    return config.get(key, DEFAULTS[module][key])


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    module = config[CONF_RADIO_MODULE]
    defaults = DEFAULTS[module]

    cs_pin = config.get(CONF_CS_PIN, defaults[CONF_CS_PIN])
    irq_pin = config.get(CONF_IRQ_PIN, defaults[CONF_IRQ_PIN])
    rst_pin = config.get(CONF_RST_PIN, defaults[CONF_RST_PIN])
    busy_pin = config.get(CONF_BUSY_PIN, defaults[CONF_BUSY_PIN])
    spi_clk = config.get(CONF_SPI_CLK_PIN, defaults[CONF_SPI_CLK_PIN])
    spi_mosi = config.get(CONF_SPI_MOSI_PIN, defaults[CONF_SPI_MOSI_PIN])
    spi_miso = config.get(CONF_SPI_MISO_PIN, defaults[CONF_SPI_MISO_PIN])

    rst_value = "RADIOLIB_NC" if rst_pin == -1 else str(rst_pin)
    busy_value = "RADIOLIB_NC" if busy_pin == -1 else str(busy_pin)

    if module == RADIO_MODULE_CC1101:
        cg.add_build_flag("-DUSE_CC1101")
        cg.add_build_flag(f"-DPIN_RECEIVER_CS={cs_pin}")
        cg.add_build_flag(f"-DPIN_RECEIVER_IRQ={irq_pin}")
        cg.add_build_flag(f"-DPIN_RECEIVER_GPIO={config.get(CONF_BUSY_PIN, 5)}")
        cg.add_build_flag(f"-DPIN_RECEIVER_RST={rst_value}")
    elif module == RADIO_MODULE_SX1262:
        cg.add_build_flag("-DUSE_SX1262")
        cg.add_build_flag(f"-DPIN_RECEIVER_CS={cs_pin}")
        cg.add_build_flag(f"-DPIN_RECEIVER_IRQ={irq_pin}")
        cg.add_build_flag(f"-DPIN_RECEIVER_RST={rst_value}")
        cg.add_build_flag(f"-DPIN_RECEIVER_BUSY={busy_value}")

    if spi_clk != -1:
        cg.add_build_flag(f"-DPIN_RECEIVER_SPI_SCK={spi_clk}")
        cg.add_build_flag(f"-DPIN_RECEIVER_SPI_MOSI={spi_mosi}")
        cg.add_build_flag(f"-DPIN_RECEIVER_SPI_MISO={spi_miso}")

    if CONF_TEMPERATURE in config:
        sens = await sensor.new_sensor(config[CONF_TEMPERATURE])
        cg.add(var.set_temperature_sensor(sens))

    if CONF_HUMIDITY in config:
        sens = await sensor.new_sensor(config[CONF_HUMIDITY])
        cg.add(var.set_humidity_sensor(sens))

    if CONF_WIND_GUST in config:
        sens = await sensor.new_sensor(config[CONF_WIND_GUST])
        cg.add(var.set_wind_gust_sensor(sens))

    if CONF_WIND_SPEED in config:
        sens = await sensor.new_sensor(config[CONF_WIND_SPEED])
        cg.add(var.set_wind_speed_sensor(sens))

    if CONF_WIND_DIRECTION in config:
        sens = await sensor.new_sensor(config[CONF_WIND_DIRECTION])
        cg.add(var.set_wind_direction_sensor(sens))

    if CONF_RAIN in config:
        sens = await sensor.new_sensor(config[CONF_RAIN])
        cg.add(var.set_rain_sensor(sens))

    if CONF_UV in config:
        sens = await sensor.new_sensor(config[CONF_UV])
        cg.add(var.set_uv_sensor(sens))

    if CONF_LIGHT in config:
        sens = await sensor.new_sensor(config[CONF_LIGHT])
        cg.add(var.set_light_sensor(sens))

    if CONF_RSSI in config:
        sens = await sensor.new_sensor(config[CONF_RSSI])
        cg.add(var.set_rssi_sensor(sens))

    if CONF_BATTERY_OK in config:
        sens = await binary_sensor.new_binary_sensor(config[CONF_BATTERY_OK])
        cg.add(var.set_battery_sensor(sens))

    if CONF_SENSOR_ID in config:
        sens = await text_sensor.new_text_sensor(config[CONF_SENSOR_ID])
        cg.add(var.set_sensor_id_text_sensor(sens))

    if CONF_FILTER_SENSOR_ID in config:
        cg.add(var.set_filter_sensor_id(config[CONF_FILTER_SENSOR_ID]))

    cg.add_platformio_option("lib_deps", ["matthias-bs/BresserWeatherSensorReceiver@0.37.0"])
    cg.add_platformio_option("lib_deps", ["jgromes/RadioLib@7.4.0"])
    cg.add_platformio_option("lib_deps", ["vshymanskyy/Preferences@2.2.2"])
    cg.add_platformio_option("lib_deps", ["bblanchon/ArduinoJson@7.4.2"])
    cg.add_platformio_option("lib_ldf_mode", "deep+")
