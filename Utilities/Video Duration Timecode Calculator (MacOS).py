import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar
import os
import subprocess
import csv  # Importing csv module

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
    global durations  # Define a global list to store video details
    durations = []
    for video in video_files:
        cmd = ['/opt/homebrew/bin/ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', video]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        if output:
            try:
                duration_seconds = float(output)
                duration = format_duration(duration_seconds)
                total_seconds += duration_seconds
                listbox.insert(tk.END, f"{video}: {duration}")
                durations.append((video, duration))
            except ValueError:
                listbox.insert(tk.END, f"Error converting output to float. Video: {video}, Output: '{output}'")
        else:
            error_message = f"No duration found. Video: {video}, FFprobe error: {result.stderr.strip()}"
            listbox.insert(tk.END, error_message)

    total_duration = format_duration(total_seconds)
    if total_seconds > 0:
        listbox.insert(tk.END, f"Total Duration: {total_duration}")
        durations.append(("Total Duration", total_duration))
    else:
        listbox.insert(tk.END, "No valid video durations to total.")

def export_to_csv():
    if not durations:
        messagebox.showinfo("Export Error", "No data to export.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Duration"])
        writer.writerows(durations)
    messagebox.showinfo("Export Successful", f"Data successfully exported to {filepath}")

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

root = tk.Tk()
root.title("Video Duration Calculator")
root.geometry("800x400")  # Set initial size of window
root.resizable(True, True)  # Make the window resizable

scrollbar = Scrollbar(root)
scrollbar.grid(row=0, column=1, sticky='ns')

listbox = tk.Listbox(root, width=100, height=15, yscrollcommand=scrollbar.set)
listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

scrollbar.config(command=listbox.yview)

btn_select_folder = tk.Button(root, text="Select Folder", command=select_folder)
btn_select_folder.grid(row=1, column=0, pady=20)

btn_export_csv = tk.Button(root, text="Export to CSV", command=export_to_csv)
btn_export_csv.grid(row=1, column=0, padx=20, pady=20, sticky="e")

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)  # Makes the listbox expand

root.mainloop()
