import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_video():
    path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
    if path:
        video_path.set(path)

def select_audio():
    path = filedialog.askopenfilename(filetypes=[("Dolby Audio MP4", "*.mp4")])
    if path:
        audio_path.set(path)

def embed_audio():
    video = video_path.get()
    audio = audio_path.get()

    if not video or not audio:
        messagebox.showerror("Missing File", "Please select both video and audio files.")
        return

    output = os.path.splitext(video)[0] + "_embedded.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i", video,
        "-i", audio,
        "-map", "0:v:0",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "copy",
        output
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        messagebox.showinfo("Success", f"Embedded audio saved to:\n{output}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or str(e)
        messagebox.showerror("FFmpeg Error", f"Failed to embed audio:\n{error_msg}")

# GUI setup
root = tk.Tk()
root.title("Dolby Audio Embedder")

video_path = tk.StringVar()
audio_path = tk.StringVar()

tk.Label(root, text="Select Video File:").pack(pady=5)
tk.Entry(root, textvariable=video_path, width=60).pack()
tk.Button(root, text="Browse Video", command=select_video).pack(pady=5)

tk.Label(root, text="Select Dolby Audio MP4 File:").pack(pady=5)
tk.Entry(root, textvariable=audio_path, width=60).pack()
tk.Button(root, text="Browse Audio", command=select_audio).pack(pady=5)

tk.Button(root, text="Embed Audio", command=embed_audio, bg="green", fg="white").pack(pady=15)

root.mainloop()
