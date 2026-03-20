import socket
import threading
import json
import logging
import time

# Local module import
import protocol

def handle_client(conn, addr, data_queue, pending_commands, commands_lock):
    """
    Handles an individual client connection, processing incoming data
    and sending back a response with any pending commands.
    """
    device_id = "unknown"
    logging.info(f"Accepted connection from {addr}")
    try:
        with conn:
            # Set a timeout for the socket operations
            conn.settimeout(10.0)
            
            # Use a buffer to handle incoming data stream
            buffer = ""
            while True:
                chunk = conn.recv(1024).decode('utf-8')
                if not chunk:
                    break # Connection closed by client
                buffer += chunk
                # Check if a complete JSON object has been received (terminated by newline)
                if '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    
                    logging.info(f"Received raw data from {addr}: {message}")
                    data = json.loads(message)
                    device_id = data.get("deviceId", "unknown")
                    
                    # Place received data onto the queue for the cloud worker
                    if data:
                        data_queue.put(data)
                        logging.info(f"Queued data from {device_id} for cloud forwarding.")

                    # --- Check for and retrieve a pending command ---
                    command_to_send = protocol.COMMAND_NONE
                    if device_id != "unknown":
                        with commands_lock:
                            # Use .pop() to retrieve the command and remove it atomically
                            command_to_send = pending_commands.pop(device_id, protocol.COMMAND_NONE)
                        
                        if command_to_send != protocol.COMMAND_NONE:
                            logging.info(f"Found pending command '{command_to_send}' for {device_id}. Preparing response.")

                    # --- Prepare and send response to the device ---
                    response_data = {
                        "status": "ok",
                        "time": int(time.time()),
                        "command": command_to_send
                    }
                    response_json = json.dumps(response_data) + '\n'
                    conn.sendall(response_json.encode('utf-8'))
                    logging.info(f"Sent response to {device_id}: {response_data}")
                    break # Exit loop after processing one message
    except json.JSONDecodeError:
        logging.error(f"Received malformed JSON from {addr}")
    except socket.timeout:
        logging.warning(f"Connection from {addr} timed out.")
    except Exception as e:
        logging.error(f"An error occurred with client {addr}: {e}")
    finally:
        logging.info(f"Connection from {addr} (Device: {device_id}) closed.")


def start_receiver(data_queue, pending_commands, commands_lock):
    """
    Starts the TCP server to listen for incoming connections from hardware devices.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((protocol.SERVER_HOST, protocol.SERVER_PORT))
        s.listen()
        logging.info(
            f"Local server listening on {protocol.SERVER_HOST}:{protocol.SERVER_PORT}")
        while True:
            conn, addr = s.accept()
            # Start a new thread to handle the client connection
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, data_queue, pending_commands, commands_lock),
                daemon=True
            )
            client_thread.start()

