import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import re

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        list_videos(folder_path)

def list_videos(folder_path):
    video_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mov', '.mp4', '.avi', '.mkv', '.flv')):
                full_path = os.path.join(root, file)
                video_files.append(full_path)

    if video_files:
        get_durations(video_files)
    else:
        messagebox.showinfo("No Videos", "No video files found in the selected directory.")

def get_durations(video_files):
    total_seconds = 0
    listbox.delete(0, tk.END)
    for video in video_files:
        cmd = ['ffmpeg', '-i', video, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            duration = float(result.stdout.strip())
            total_seconds += duration
            listbox.insert(tk.END, f"{video}: {format_duration(duration)}")
        except ValueError:
            listbox.insert(tk.END, f"Error processing {video}: Duration could not be determined")

    if total_seconds > 0:
        listbox.insert(tk.END, f"Total Duration: {format_duration(total_seconds)}")
    else:
        listbox.insert(tk.END, "No valid video durations to total.")

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

root = tk.Tk()
root.title("Video Duration Calculator")

listbox = tk.Listbox(root, width=100, height=15)
listbox.pack(pady=20)

btn_select_folder = tk.Button(root, text="Select Folder", command=select_folder)
btn_select_folder.pack(pady=20)

root.mainloop()
