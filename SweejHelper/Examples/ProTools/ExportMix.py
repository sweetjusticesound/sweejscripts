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
    "presetPath": "/path/to/preset/",  # Replace with actual path to preset, make sure ends in /
    "fileName": "myMix",  # Replace with desired file name for the exported mix
    "fileType": "WAV",  # Choose from: "None", "MOV", "WAV", "AIFF", "MP3", "MXFOPAtom", "WAVADM"
    "filesList": "",  # Replace with list of files (deprecated)
    "mixSourceList": "source1,source2",  # Replace with list of mix sources
    "audioInfo": {  # Audio parameters
        "compressionType": "None",  # Choose from: "None", "PCM"
        "exportFormat": "Interleaved",  # Choose from: "None", "Mono", "MultipleMono", "Interleaved"
        "bitDepth": "Bit24",  # Set bit depth
        "sampleRate": "SR_48000",  # Set sample rate (Hz). Choose from: "SR_None", "SR_44100", "SR_48000", "SR_96000", "SR_176400", "SR_192000", "SR_88200"
        "padToFrameBoundary": "True",  # Choose from: "None", "False", "True"
        "deliveryFormat": "SingleFile"  # Choose from: "None", "FilePerMixSource", "SingleFile"
    },
    "videoInfo": {  # Video parameters
        "includeVideo": "False",  # Choose from: "None", "False", "True"
        "videoExportOptions": "Transcode",  # Choose from: "None", "SameAsSource", "Transcode"
        "replaceTimeCodeTrack": "False",  # Choose from: "None", "False", "True"
        "codecInfo": {
            "codecName": "H.264",  # Replace with actual codec name
            "propertyList": "property1,property2"  # Replace with list of codec properties
        }
    },
    "locationInfo": {  # Location parameters
        "importAfterBounce": "False",  # Choose from: "None", "False", "True"
        "importOptions": {
            "importDestination": "NewTrack",  # Choose from: "None", "MainVideoTrack", "NewTrack", "ClipList"
            "importLocation": "SessionStart",  # Choose from: "None", "SessionStart", "SongStart", "Selection", "Spot"
            "gapsBetweenClips": 2,  # Specify gaps between clips (seconds)
            "importAudioFromFile": "True",  # Choose from: "None", "False", "True"
            "removeExistingVideoTracks": "True",  # Choose from: "None", "False", "True"
            "removeExistingVideoClips": "True",  # Choose from: "None", "False", "True"
            "clearDestinationVideoTrackPlaylist": "True"  # Choose from: "None", "False", "True"
        },
        "fileDestination": "SessionFolder",  # Choose from: "None", "SessionFolder", "Directory"
        "directory": "/path/to/directory/"  # Replace with actual directory path, make sure ends in /
    },
    "dolbyAtmosInfo": {  # Dolby Atmos parameters
        "firstFrameOfAction": "False",  # Choose from: "None", "False", "True"
        "timeCodeValue": "00:00:00:00",  # Replace with actual time code value
        "frameRate": 24,  # Specify frame rate (fps)
        "propertyList": "property1,property2"  # Replace with list of Dolby Atmos properties
    },
    "offlineBounce": "True"  # Choose from: "None", "False", "True"
}

# Convert the arguments to a JSON string
arguments_json = json.dumps(arguments)

# URL encode the JSON string
arguments_encoded = urllib.parse.quote(arguments_json, safe='')

# Prepare the message
message = f'sweejhelper://proToolsFunction/exportMix/{request_id}?arguments={arguments_encoded}'

# Send a request to export the mix
send_message_to_sweejhelper(message)