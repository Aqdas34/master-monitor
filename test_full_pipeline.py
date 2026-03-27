import time
import requests

# This is the test payload exactly как it was from your device
payload = {
    'deviceId': 'MM-TEST-DEVICE-01', 
    'data': [
        {
            'SystemErrorCode': 0, 
            'SdSpaceUsed': 1024, 
            'SdSpaceLeft': 8192, 
            'SdDetect': 1, 
            'BatteryLevel': 85, 
            'Alarm': 0, 
            'Smoke': 12, 
            'CarbonMonoxide': 5, 
            'Gas': 110.5, 
            'AQI': 45.2, 
            'MotionPresence': 0, 
            'NoisePresence': 0, 
            'NoiseLevel': 30.0, 
            'Humidity': 48, 
            'Temperature': 22.4, 
            'Pressure': 1012.3, 
            'HornHush': 0, 
            'Test': 0, 
            'Time': int(time.time())
        }
    ]
}

# The address of your local Master Monitor Server
# gateway_url = "http://127.0.0.1:49441/"
# In test_full_pipeline.py
gateway_url = "http://157.173.120.125:49441/" # <-- Replace 127.0.0.1 with your real VPS IP

# The mandatory security header
headers = {
    "X-API-Key": "MM-PROD-SECURE-KEY-827-XVZ",
    "Content-Type": "application/json"
}

print(f"--- INITIALIZING LOCAL PIPELINE TEST ---")
print(f"STEP 1: Sending data to Master Monitor ({gateway_url})...")

try:
    response = requests.post(gateway_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("✅ SUCCESS: Data accepted by Master Monitor.")
        print("Response:", response.json())
        print("\nSTEP 2: Data will now be forwarded to the Cloud API (Port 8000) automatically.")
        print("Watch your Server Logs for the 'Successfully sent to cloud' message!")
    else:
        print(f"❌ FAILED: Server returned code {response.status_code}")
        print("Error detail:", response.text)

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
