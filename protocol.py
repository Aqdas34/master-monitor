# This file defines constants used across the server application to ensure consistency.

# --- Network Configuration ---
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 49441

# --- mDNS Configuration ---
MDNS_SERVICE_NAME = "globalalertz-mmserver0"
MDNS_SERVICE_TYPE = "_http._tcp.local."

# --- Cloud Endpoint ---
# Development: points to the local Cloud Ingestion API running on this machine
# Production:  change to "http://mm_interface.globalalertz.com/rx"
CLOUD_ENDPOINT_URL = "http://localhost:8000/rx"

# --- API Key (must match MASTER_MONITOR_API_KEY on the cloud server) ---
CLOUD_API_KEY = "dev-key-change-me-in-production"

# --- Commands ---
# These strings are used in the JSON communication between the local server,
# the cloud, and the ESP32 devices.
COMMAND_NONE = "none"
COMMAND_TEST = "test"
COMMAND_HUSH = "hush"
COMMAND_EXTERNAL_ALARM = "external_alarm"


# --- Example Payload Data (for reference and testing) ---

EXAMPLE_PAYLOAD = {
  "deviceId": "MM-1A2B3C4D5E6F",
  "data": [
    {
      "SystemErrorCode": 0,
      "SdSpaceUsed": 512,
      "SdSpaceLeft": 9876,
      "SdDetect": 1,
      "BatteryLevel": 95,
      "Alarm": 0,
      "Smoke": 5,
      "CarbonMonoxide": 2,
      "Gas": 150,
      "AQI": 25,
      "MotionPresence": 1,
      "NoisePresence": 0,
      "NoiseLevel": 35,
      "Humidity": 45,
      "Temperature": 21,
      "Pressure": 1012,
      "HornHush": 0,
      "Test": 0,
      "Time": 1729257300
    }
  ]
}

