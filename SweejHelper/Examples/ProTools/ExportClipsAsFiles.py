import json
import urllib.parse
import uuid
import time
import socket

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

# Prepare the arguments
arguments = {
    "filePath": "<filePath>",  # Replace <filePath> with actual value
    "format": "Interleaved",  # Choose from: "None", "Mono", "MultipleMono", "Interleaved"
    "fileType": "WAV",  # Choose from: "WAV", "AIFF", "MXF"
    "bitDepth": "Bit24",  # Choose from: "None", "Bit16", "Bit24", "Bit32Float"
    "duplicateNames": "AutoRenaming",  # Choose from: "AutoRenaming", "ReplacingWithNewFiles"
    "enforceAvidCompatibility": True  # Replace <enforceAvidCompatibility> with either True or False
}

# Convert the arguments to a JSON string
arguments_json = json.dumps(arguments)

# URL encode the JSON string
arguments_encoded = urllib.parse.quote(arguments_json, safe='')

# Prepare the message
message = f'sweejhelper://proToolsFunction/exportClipsAsFiles/{request_id}?arguments={arguments_encoded}'

# Send a request to export clips as files
send_message_to_sweejhelper(message)