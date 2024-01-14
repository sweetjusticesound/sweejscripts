import tkinter as tk
from tkinter import messagebox
import os
import shutil
import zipfile
import getpass
from datetime import datetime

def get_target_path():
    username = os.getenv("SUDO_USER") or getpass.getuser()
    v6_path = f"/Users/{username}/Library/Application Support/SoundminerV6"
    v5_path = f"/Users/{username}/Library/Application Support/SoundminerV5"
    if os.path.exists(v6_path):
        return v6_path
    elif os.path.exists(v5_path):
        return v5_path
    else:
        return None

def move_files(src_folder, dest_folder):
    if not os.path.exists(src_folder):
        messagebox.showerror("Error", f"Source folder '{src_folder}' does not exist!")
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for filename in os.listdir(src_folder):
        src_path = os.path.join(src_folder, filename)
        dest_path = os.path.join(dest_folder, filename)

        if os.path.isfile(src_path) or os.path.isdir(src_path):
            shutil.move(src_path, dest_path)

    messagebox.showinfo("Success", f"Items moved from {src_folder} to {dest_folder}")

def move_to_unused():
    move_files("/Library/Audio/Plug-Ins/Components", "/Library/Audio/Plug-Ins/Components (Unused)")

def move_from_unused():
    move_files("/Library/Audio/Plug-Ins/Components (Unused)", "/Library/Audio/Plug-Ins/Components")

def backup_sqlite():
    target_path = get_target_path()
    if target_path is None:
        messagebox.showerror("Error", "Soundminer folder doesn't exist.")
        return

    sqlite_file = os.path.join(target_path, "Plugins.sqlite")
    if not os.path.exists(sqlite_file):
        messagebox.showerror("Error", "Plugins.sqlite file doesn't exist.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_filename = f"plugins_{timestamp}.zip"
    backup_filepath = os.path.join(target_path, backup_filename)

    with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(sqlite_file, "Plugins.sqlite")

    messagebox.showinfo("Success", f"Backup created at {backup_filepath}")

def delete_sqlite():
    target_path = get_target_path()
    if target_path is None:
        messagebox.showerror("Error", "Soundminer folder doesn't exist.")
        return

    sqlite_file = os.path.join(target_path, "Plugins.sqlite")
    if not os.path.exists(sqlite_file):
        messagebox.showerror("Error", "Plugins.sqlite file doesn't exist.")
        return

    os.remove(sqlite_file)
    messagebox.showinfo("Success", "Plugins.sqlite deleted.")

# Create the Tkinter window
root = tk.Tk()
root.title("Move Components")

# Create buttons and place them on the window
button1 = tk.Button(root, text="Move Components to Components (Unused) folder", command=move_to_unused)
button1.pack(fill=tk.BOTH, padx=5, pady=5)

button3 = tk.Button(root, text="Backup Plugins.sqlite", command=backup_sqlite)
button3.pack(fill=tk.BOTH, padx=5, pady=5)

button4 = tk.Button(root, text="Delete Plugins.sqlite", command=delete_sqlite)
button4.pack(fill=tk.BOTH, padx=5, pady=5)

button2 = tk.Button(root, text="Move Components (Unused) to Components", command=move_from_unused)
button2.pack(fill=tk.BOTH, padx=5, pady=5)

# Run the Tkinter event loop
root.mainloop()
