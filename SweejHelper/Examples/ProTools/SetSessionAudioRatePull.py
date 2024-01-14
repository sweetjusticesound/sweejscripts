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

# Valid audioRatePull values: "SRP_None", "SRP_Up01", "SRP_Down01", "SRP_Up4", "SRP_Up4Up01", "SRP_Up4Down01", "SRP_Down4", "SRP_Down4Up01", "SRP_Down4Down01"
audioRatePull = "SRP_None"

arguments = {"audioRatePull": audioRatePull}
arguments_string = json.dumps(arguments)

request_id = str(uuid.uuid4())
url = f'sweejhelper://proToolsFunction/setSessionAudioRatePullSettings/{request_id}?arguments={urllib.parse.quote(arguments_string)}'
send_message_to_sweejhelper(url)