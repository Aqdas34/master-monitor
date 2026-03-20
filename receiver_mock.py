import time
import threading
import logging
import random

# Local module import
import protocol

def generate_mock_data(device_id):
    """Generates a single mock data object."""
    return {
        "SystemErrorCode": 0,
        "SdSpaceUsed": random.randint(100, 1000),
        "SdSpaceLeft": random.randint(9000, 10000),
        "SdDetect": 1,
        "BatteryLevel": random.randint(5, 100),
        "Alarm": random.choice([0, 1]),
        "Smoke": random.randint(2, 50),
        "CarbonMonoxide": random.randint(1, 15),
        "Gas": random.randint(100, 200),
        "AQI": random.randint(10, 60),
        "MotionPresence": random.choice([0, 1]),
        "NoisePresence": random.choice([0, 1]),
        "NoiseLevel": random.randint(30, 80),
        "Humidity": random.randint(30, 60),
        "Temperature": random.randint(18, 25),
        "Pressure": random.randint(990, 1020),
        "HornHush": 0,
        "Test": 0,
        "Time": int(time.time())
    }

def start_receiver(data_queue, pending_commands, commands_lock):
    """
    Simulates hardware sending data at regular intervals.
    Accepts pending_commands and commands_lock for interface consistency but does not use them.
    """
    logging.info("Starting MOCK data generator...")
    mock_device_ids = ["MM-MOCKDEVICE01", "MM-MOCKDEVICE02"]
    
    while True:
        # Every 10 seconds, generate data for a random mock device
        time.sleep(10)
        
        # Choose a random device to send data
        chosen_device = random.choice(mock_device_ids)
        
        payload = {
            "deviceId": chosen_device,
            "data": [generate_mock_data(chosen_device)]
        }
        
        logging.info(f"MOCK: Generating data for device {chosen_device}")
        data_queue.put(payload)

