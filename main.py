import logging
import threading
import time
from queue import Queue
import requests
from zeroconf import ServiceInfo, Zeroconf
import socket

# Local module imports
import protocol
# --- Main Application Toggle ---
# Set to True to use the mock receiver for testing, False for real hardware.
USE_MOCK_RECEIVER = True

if USE_MOCK_RECEIVER:
    from receiver_mock import start_receiver
else:
    from receiver import start_receiver

# --- Global Shared State ---
# Thread-safe queue to hold data received from devices, ready to be forwarded.
data_buffer = Queue()
# Thread-safe dictionary to hold pending commands for devices.
# Key: deviceId, Value: command_string
pending_commands = {}
commands_lock = threading.Lock()


def setup_logging():
    """Configures the logging format for the application."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def get_local_ip():
    """Finds the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def register_mdns_service():
    """Registers the server on the local network using mDNS/Zeroconf."""
    local_ip = get_local_ip()
    info = ServiceInfo(
            protocol.MDNS_SERVICE_TYPE,
            f"{protocol.MDNS_SERVICE_NAME}.{protocol.MDNS_SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=protocol.SERVER_PORT,
            properties={'path': '/'},
            server=f"{protocol.MDNS_SERVICE_NAME}.local."
        )
    zeroconf = Zeroconf()
    logging.info(
        f"Registering mDNS service '{info.name}' on {local_ip}:{protocol.SERVER_PORT}...")
    try:
        # allow_name_change=True will automatically rename the service if the name is taken
        zeroconf.register_service(info, allow_name_change=True)
    except Exception as e:
        zeroconf.close()
        raise e
    return zeroconf, info


def forward_to_cloud(payload, device_id):
    """
    Sends the provided data payload to the central cloud server.
    If the cloud returns a command, it is stored for the next device communication.
    """
    try:
        logging.info(f"Forwarding {len(payload.get('data', []))} data point(s) for {device_id} to cloud...")
        response = requests.post(
            protocol.CLOUD_ENDPOINT_URL,
            json=payload,
            headers={"X-API-Key": protocol.CLOUD_API_KEY},
            timeout=10
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Process the response from the cloud
        cloud_response = response.json()
        logging.info(f"Successfully sent data for {device_id}. Cloud response: {cloud_response}")

        # Check for and store any commands from the cloud
        cloud_command = cloud_response.get("command", protocol.COMMAND_NONE)
        if cloud_command != protocol.COMMAND_NONE:
            with commands_lock:
                logging.info(f"Storing command '{cloud_command}' for device {device_id}.")
                pending_commands[device_id] = cloud_command

        return True # Indicate success
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not send data for {device_id} to cloud: {e}")
        return False # Indicate failure


def cloud_worker():
    """
    A worker thread that continuously processes the data buffer, forwarding data to the cloud.
    It handles data aggregation and retries.
    """
    local_buffer = {} # Key: deviceId, Value: list of data objects
    
    while True:
        # Move all items from the shared queue to a local buffer
        while not data_buffer.empty():
            item = data_buffer.get()
            device_id = item.get("deviceId")
            data_points = item.get("data", [])
            
            if device_id and data_points:
                if device_id not in local_buffer:
                    local_buffer[device_id] = []
                local_buffer[device_id].extend(data_points)
                logging.info(f"Buffered {len(data_points)} new data point(s) for {device_id}. Total buffered: {len(local_buffer[device_id])}")

        # Try to send the buffered data for each device
        if local_buffer:
            logging.info("Processing local buffer for cloud forwarding...")
            # Iterate over a copy of keys to allow modification during iteration
            for device_id in list(local_buffer.keys()):
                payload = {
                    "deviceId": device_id,
                    "data": local_buffer[device_id]
                }
                
                if forward_to_cloud(payload, device_id):
                    # If successful, clear the buffer for this device
                    logging.info(f"Successfully forwarded buffer for {device_id}. Clearing local buffer.")
                    del local_buffer[device_id]
                else:
                    # If failed, keep the data in the buffer for the next attempt
                    logging.warning(f"Failed to forward buffer for {device_id}. Data will be retried.")
        
        # Wait before checking the queue again to avoid busy-waiting
        time.sleep(5)


def main():
    """Main function to start the server and its components."""
    setup_logging()
    
    # Start the cloud forwarding worker thread
    cloud_thread = threading.Thread(target=cloud_worker, daemon=True)
    cloud_thread.start()
    logging.info("Cloud forwarding worker started.")

    # Start the appropriate TCP receiver
    receiver_type = "mock" if USE_MOCK_RECEIVER else "real hardware"
    logging.info(f"Starting TCP receiver for {receiver_type}...")
    # Pass the shared data queue and command dictionary to the receiver
    receiver_thread = threading.Thread(target=start_receiver, args=(data_buffer, pending_commands, commands_lock), daemon=True)
    receiver_thread.start()

    # Register mDNS service and keep the main thread alive
    zeroconf_obj = None
    info = None
    try:
        zeroconf_obj, info = register_mdns_service()
    except Exception as e:
        logging.warning(f"Could not register mDNS service: {e}. The server will still function, but local discovery is disabled.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    finally:
        if zeroconf_obj and info:
            try:
                zeroconf_obj.unregister_service(info)
                zeroconf_obj.close()
                logging.info("mDNS service unregistered.")
            except Exception as e:
                logging.error(f"Error during mDNS shutdown: {e}")
        logging.info("Server stopped.")


if __name__ == "__main__":
    main()

