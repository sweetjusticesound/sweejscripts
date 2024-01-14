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
    client_socket.connect(('localhost', 65500))
    
    print("Sending message to the server...")
    client_socket.send(message.encode('utf-8'))

    print("Shutting down write part of the socket...")
    client_socket.shutdown(socket.SHUT_WR)

    client_socket.setblocking(0)

    start_time = time.time()
    response = b""

    while True:
        try:
            print("Attempting to receive data from the server...")
            chunk = client_socket.recv(4096)
            if chunk:
                print("Received data chunk from the server.")
                response += chunk
            else:
                break
        except socket.error:
            print("No data received, sleeping for a bit before retrying...")
            time.sleep(2)

    print("Closing client socket connection...")
    client_socket.close()

    if response:
        try:
            response_json = json.loads(response.decode('utf-8'))
            print(f"Received response: {response_json}")
        except json.JSONDecodeError:
            print("Did not receive a valid JSON response from the server")

request_id = str(uuid.uuid4())

arguments = {
    "sessionPath": "/path/to/session",
    "importType": "Audio",
    "audioData": {
        "audioOptions": "ForceToTargetSessionFormat",
        "audioHandleSize": 1024,
        "audioOperations": "Default",
        "destination": "ClipList",
        "location": "Spot",
        "filesList": ["/path/to/media/file1", "/path/to/media/file2"]
    },
    "videoOptions": "CopyFromSource",
    "matchOptions": "ImportAsNewTrack",
    "playlistOptions": "DoNotImport",
    "trackDataPresetPath": "/path/to/preset",
    "clipGain": True,
    "clipsAndMedia": True,
    "volumeAutomation": True,
    "timeCodeMappingOptions": "MapStartTimeCodeTo",
    "timeCodeMappingStartTime": "00:00:00:00",
    "adjustSessionStartTimeToMatchSource": True,
}

json_arguments = json.dumps(arguments)
encoded_arguments = urllib.parse.quote(json_arguments)
send_message_to_sweejhelper(f'sweejhelper://proToolsFunction/importMedia/{request_id}?arguments={encoded_arguments}')
