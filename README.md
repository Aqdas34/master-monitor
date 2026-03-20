# Local Server for ESP32 Sensor Hub

This Python application acts as a local gateway server for ESP32 sensor devices. It listens for incoming TCP connections, receives sensor data, buffers it, and forwards it to a central cloud server.

## Features

- mDNS Service Discovery: Broadcasts its presence on the local network as globalalertz-mmserver0.local so devices can connect without a hardcoded IP address.
- TCP Data Reception: Listens for JSON payloads from hardware devices.
- Data Buffering & Retries: If the cloud server is unreachable, incoming data is buffered locally. Buffered data is automatically combined with new data and re-sent on the next transmission cycle.
- Multi-threaded: Handles multiple device connections concurrently without blocking.
- Mock Mode: Includes a mock data generator for testing the server and cloud connection without needing physical hardware.

## File Structure

The server is organized into the following files:

- main.py: The main application entry point. It handles mDNS registration, cloud forwarding, and starts the receiver module.
- receiver.py: Handles the TCP server socket, listens for connections from real ESP32 devices, and processes incoming data.
- receiver_mock.py: A drop-in replacement for receiver.py that generates simulated hardware data at regular intervals for testing purposes.
- protocol.py: A central configuration file defining ports, mDNS names, cloud endpoints, and command constants.
- requirements.txt: A list of all the Python dependencies required to run the server.

## Setup and Installation

1. Prerequisites: Ensure you have Python 3.6+ installed.
2. Create a Virtual Environment (Recommended).
3. Install Dependencies: `pip install -r requirements.txt`.

## Running the Server

1. Start the Server:
   `python main.py`

## CI/CD and Deployment
Automated deployment is configured via **GitHub Actions**.

1. See [cicd_setup_guide.md](cicd_setup_guide.md) for instructions on setting up SSH keys and secrets.
2. The workflow file is located in `.github/workflows/deploy_mm_server.yml`.
3. Pushing to the `main` branch will automatically deploy to your VPS at `157.173.120.125`.

## Running in Mock Mode
To test without hardware, set `USE_MOCK_RECEIVER = True` at the top of `main.py`.