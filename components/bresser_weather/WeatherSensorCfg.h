///////////////////////////////////////////////////////////////////////////////////////////////////
// WeatherSensorCfg.h
//
// Bresser 5-in-1/6-in-1/7-in-1 868 MHz Weather Sensor Radio Receiver
// based on CC1101, SX1276/RFM95W, SX1262 or LR1121 and ESP32/ESP8266
//
// This version lives here to override the one in the library.
// It is copied to the library folder during build by pre_build.py
//
///////////////////////////////////////////////////////////////////////////////////////////////////

#if !defined(WEATHER_SENSOR_CFG_H)
#define WEATHER_SENSOR_CFG_H

#include <Arduino.h>

// ------------------------------------------------------------------------------------------------
// --- Weather Sensors ---
// ------------------------------------------------------------------------------------------------
#define MAX_SENSORS_DEFAULT 1

#define SENSOR_IDS_EXC { }
#define SENSOR_IDS_INC { }
#define MAX_SENSOR_IDS 12

#define WIND_DATA_FLOATINGPOINT
#define WIND_DATA_FIXEDPOINT

#define BRESSER_5_IN_1
#define BRESSER_6_IN_1
#define BRESSER_7_IN_1
#define BRESSER_LIGHTNING
#define BRESSER_LEAKAGE

// ------------------------------------------------------------------------------------------------
// --- Rain Gauge / Lightning sensor data retention during deep sleep ---
// ------------------------------------------------------------------------------------------------

#if !defined(INSIDE_UNITTEST)
    #if defined(ESP32)
        #define RAINGAUGE_USE_PREFS
        #define LIGHTNING_USE_PREFS
    #else
        #define RAINGAUGE_USE_PREFS
        #define LIGHTNING_USE_PREFS
    #endif
#endif

#if defined(USE_CC1101)
#define RADIO_CHIP CC1101
#elif defined(USE_SX1276)
#define RADIO_CHIP SX1276
#elif defined(USE_SX1262)
#define RADIO_CHIP SX1262
// WeatherSensor.cpp uses PIN_RECEIVER_GPIO as the 4th Module() arg (BUSY pin for SX1262)
#if defined(PIN_RECEIVER_BUSY) && !defined(PIN_RECEIVER_GPIO)
#define PIN_RECEIVER_GPIO PIN_RECEIVER_BUSY
#endif
#elif defined(USE_LR1121)
#define RADIO_CHIP LR1121
#else
#pragma message("No radio chip selected!")
#endif

// ------------------------------------------------------------------------------------------------
// --- Debug Logging Output ---
// ------------------------------------------------------------------------------------------------
#if defined(ESP8266) || defined(ARDUINO_ARCH_RP2040)
    #define ARDUHAL_LOG_LEVEL_NONE      0
    #define ARDUHAL_LOG_LEVEL_ERROR     1
    #define ARDUHAL_LOG_LEVEL_WARN      2
    #define ARDUHAL_LOG_LEVEL_INFO      3
    #define ARDUHAL_LOG_LEVEL_DEBUG     4
    #define ARDUHAL_LOG_LEVEL_VERBOSE   5

    #if defined(ARDUINO_ARCH_RP2040) && defined(DEBUG_RP2040_PORT)
        #define DEBUG_PORT DEBUG_RP2040_PORT
    #elif defined(DEBUG_ESP_PORT)
        #define DEBUG_PORT DEBUG_ESP_PORT
    #endif

    #if !defined(CORE_DEBUG_LEVEL)
        #define CORE_DEBUG_LEVEL ARDUHAL_LOG_LEVEL_INFO
    #endif

    #if defined(DEBUG_PORT) && CORE_DEBUG_LEVEL > ARDUHAL_LOG_LEVEL_NONE
        #define log_e(...) { DEBUG_PORT.printf("%s(), l.%d: ",__func__, __LINE__); DEBUG_PORT.printf(__VA_ARGS__); DEBUG_PORT.println(); }
     #else
        #define log_e(...) {}
     #endif
    #if defined(DEBUG_PORT) && CORE_DEBUG_LEVEL > ARDUHAL_LOG_LEVEL_ERROR
        #define log_w(...) { DEBUG_PORT.printf("%s(), l.%d: ", __func__, __LINE__); DEBUG_PORT.printf(__VA_ARGS__); DEBUG_PORT.println(); }
     #else
        #define log_w(...) {}
     #endif
    #if defined(DEBUG_PORT) && CORE_DEBUG_LEVEL > ARDUHAL_LOG_LEVEL_WARN
        #define log_i(...) { DEBUG_PORT.printf("%s(), l.%d: ", __func__, __LINE__); DEBUG_PORT.printf(__VA_ARGS__); DEBUG_PORT.println(); }
     #else
        #define log_i(...) {}
     #endif
    #if defined(DEBUG_PORT) && CORE_DEBUG_LEVEL > ARDUHAL_LOG_LEVEL_INFO
        #define log_d(...) { DEBUG_PORT.printf("%s(), l.%d: ", __func__, __LINE__); DEBUG_PORT.printf(__VA_ARGS__); DEBUG_PORT.println(); }
     #else
        #define log_d(...) {}
     #endif
    #if defined(DEBUG_PORT) && CORE_DEBUG_LEVEL > ARDUHAL_LOG_LEVEL_DEBUG
        #define log_v(...) { DEBUG_PORT.printf("%s(), l.%d: ", __func__, __LINE__); DEBUG_PORT.printf(__VA_ARGS__); DEBUG_PORT.println(); }
     #else
        #define log_v(...) {}
     #endif

#endif

#define STR_HELPER(x) #x
#define STR(x) STR_HELPER(x)
#define RECEIVER_CHIP "[" STR(RADIO_CHIP) "]"
#pragma message("Receiver chip: " RECEIVER_CHIP)

#endif
