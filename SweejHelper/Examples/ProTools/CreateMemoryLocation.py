import sys
import socket
import json
import uuid
import time
import urllib.parse
import os

print(sys.version)
print(sys.executable)

def send_message_to_sweejhelper(message):
    print(f"Sending URL: {message}")
    
    print("Creating socket connection...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print("Connecting to the server...")
    client_socket.connect(('localhost', 65500))  # use the same port number as in your Swift application
    
    print("Sending message to the server...")
    client_socket.send(message.encode('utf-8'))

    print("Shutting down write part of the socket...")
    client_socket.shutdown(socket.SHUT_WR)

    # Set a timeout for receiving the response
    client_socket.setblocking(0)  # non-blocking mode

    start_time = time.time()
    response = b""

    while True:
        try:
            print("Attempting to receive data from the server...")
            chunk = client_socket.recv(4096)  # receive data from the server
            if chunk:
                print("Received data chunk from the server.")
                response += chunk
            else:
                # No more data to receive
                break
        except socket.error:
            # No data received, sleep for a bit before retrying
            print("No data received, sleeping for a bit before retrying...")
            time.sleep(2)  # Add a delay to allow server to finish receiving

    print("Closing client socket connection...")
    client_socket.close()

    # Parse the response as a JSON object
    if response:
        try:
            response_json = json.loads(response.decode('utf-8'))
            print(f"Received response: {response_json}")
        except json.JSONDecodeError:
            print("Did not receive a valid JSON response from the server")

# Generate a unique request id
request_id = str(uuid.uuid4())

# Replace the arguments with the appropriate values for your memory location.
arguments = {
    "number": 1,  # Any integer value
    "name": "Test SweejHelper Marker",  # Any string value
    "startTime": "00:01:00:00",  # Time string in format 'HH:MM:SS:FF'
    "endTime": "00:01:00:00",  # Time string in format 'HH:MM:SS:FF'
    "timeProperties": "TP_Marker",  # Options: "TP_Marker", "TP_Selection", "TP_None"
    "reference": "MLR_Absolute",  # Options: "MLR_BarBeat", "MLR_Absolute"
    "zoomSettings": True,  # Boolean value
    "prePostRollTimes": False,  # Boolean value
    "trackVisibility": True,  # Boolean value
    "trackHeights": False,  # Boolean value
    "groupEnables": True,  # Boolean value
    "windowConfiguration": False,  # Boolean value
    "windowConfigurationIndex": 0,  # Any integer value
    "windowConfigurationName": "Default",  # Any string value
    "comments": "SweejHelper FTW!"  # Any string value
}

json_arguments = json.dumps(arguments)
encoded_arguments = urllib.parse.quote(json_arguments)
send_message_to_sweejhelper(f'sweejhelper://proToolsFunction/createMemoryLocation/{request_id}?arguments={encoded_arguments}')
