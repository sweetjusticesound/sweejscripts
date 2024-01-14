import sys
import socket
import json
import uuid
import time
import urllib.parse
import os

def send_message_to_sweejhelper(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65500))
    client_socket.send(message.encode('utf-8'))
    client_socket.shutdown(socket.SHUT_WR)
    client_socket.setblocking(0)
    start_time = time.time()
    response = b""
    while True:
        try:
            chunk = client_socket.recv(4096)
            if chunk:
                response += chunk
            else:
                break
        except socket.error:
            time.sleep(2)
    client_socket.close()
    if response:
        try:
            response_json = json.loads(response.decode('utf-8'))
            print(f"Received response: {response_json}")
        except json.JSONDecodeError:
            print("Did not receive a valid JSON response from the server")

# Example CreateNewTracks arguments
arguments = {
    "numberOfTracks": 4,
    "trackName": "MyNewTrack",
    "trackFormat": "Mono",
    "trackType": "Audio",
    "trackTimebase": "Samples"
}

arguments_string = json.dumps(arguments)
request_id = str(uuid.uuid4())
url = f'sweejhelper://proToolsFunction/createNewTracks/{request_id}?arguments={urllib.parse.quote(arguments_string)}'
send_message_to_sweejhelper(url)
