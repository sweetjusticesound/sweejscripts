import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys

def download_and_convert():
    url = url_entry.get()
    format_choice = format_var.get()
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    if not url:
        messagebox.showerror("Error", "Please enter a video URL")
        return

    try:
        # Download video using yt-dlp
        download_command = f'yt-dlp -o "{downloads_path}/%(title)s.%(ext)s" {url}'
        subprocess.run(download_command, shell=True, check=True)

        # Find downloaded file (assuming mp4 or webm format)
        for file in os.listdir(downloads_path):
            if file.endswith(('.mp4', '.webm')):
                input_file = os.path.join(downloads_path, file)
                output_file = os.path.splitext(input_file)[0] + f'.{format_choice}'

                # Convert to selected format using FFmpeg
                convert_command = f'ffmpeg -i "{input_file}" "{output_file}"'
                subprocess.run(convert_command, shell=True, check=True)

                # Remove the original video file
                os.remove(input_file)
                break

        messagebox.showinfo("Success", f"Video downloaded and converted to {format_choice.upper()} successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Set up the Tkinter window
window = tk.Tk()
window.title("Video Downloader and Converter")

# URL entry
url_label = ttk.Label(window, text="Video URL:")
url_label.pack()
url_entry = ttk.Entry(window, width=50)
url_entry
.pack()

Format dropdown
format_label = ttk.Label(window, text="Select File Format:")
format_label.pack()
format_var = tk.StringVar()
format_dropdown = ttk.Combobox(window, textvariable=format_var, state="readonly")
format_dropdown['values'] = ('wav', 'flac')
format_dropdown.pack()

Download button
download_button = ttk.Button(window, text="Download and Convert", command=download_and_convert)
download_button.pack()

Run the Tkinter loop
window.mainloop()