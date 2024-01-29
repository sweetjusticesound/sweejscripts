import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from datetime import datetime

def convert_videos():
    directory = filedialog.askdirectory()
    if not directory:
        return

    # Create a new folder for converted videos
    date_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_directory = os.path.join(directory, f'converted_{date_stamp}')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    preset = preset_var.get()
    crf = crf_var.get()
    framerate = framerate_var.get()

    for file in os.listdir(directory):
        if file.endswith(".mp4"):
            input_file = os.path.join(directory, file)
            output_file = os.path.join(output_directory, file[:-4] + '.mov')

            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-c:v', 'libx264',
                '-preset', preset,
                '-crf', str(crf),
                '-r', str(framerate),
                '-c:a', 'aac',
                '-b:a', '320k',
                '-movflags', '+faststart',
                output_file
            ]

            subprocess.run(cmd)

    messagebox.showinfo("Conversion Complete", "All videos have been converted.")

# Creating the main window
root = tk.Tk()
root.title("MP4 to MOV Converter")

# Variables
preset_var = tk.StringVar(value='fast')
crf_var = tk.IntVar(value=23)
framerate_var = tk.DoubleVar(value=30)

# Widgets
tk.Label(root, text="Preset:").pack()
preset_entry = tk.Entry(root, textvariable=preset_var)
preset_entry.pack()

tk.Label(root, text="CRF (18-28):").pack()
crf_entry = tk.Entry(root, textvariable=crf_var)
crf_entry.pack()

tk.Label(root, text="Frame Rate:").pack()
framerate_entry = tk.Entry(root, textvariable=framerate_var)
framerate_entry.pack()

convert_button = tk.Button(root, text="Convert Videos", command=convert_videos)
convert_button.pack()

# Run the application
root.mainloop()
