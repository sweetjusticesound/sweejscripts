import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os

def open_file_dialog():
    filename = filedialog.askopenfilename()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, filename)

def open_directory_dialog():
    directory = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, directory)

def update_progress(message):
    progress_label.config(text=message)
    app.update()

def convert_videos():
    source = source_entry.get()
    output_dir = output_entry.get()
    output_filename = output_filename_entry.get()
    min_br = min_bitrate_entry.get()
    max_br = max_bitrate_entry.get()
    step_br = step_bitrate_entry.get()

    try:
        min_br_int = int(min_br)
        max_br_int = int(max_br)
        step_br_int = int(step_br)

        # Ensure the bitrate values and output filename are valid
        if min_br_int < 10000 or max_br_int > 40000 or step_br_int <= 0 or not output_filename:
            raise ValueError("Invalid input values.")

        for br in range(min_br_int, max_br_int + 1, step_br_int):
            bitrate = f"{br}k"
            transcoded_file = f"{output_dir}/{output_filename}_{bitrate}.mp4"
            update_progress(f"Transcoding at bitrate: {bitrate}")
            subprocess.run(["ffmpeg", "-i", source, "-c:v", "hevc", "-b:v", bitrate, "-c:a", "copy", transcoded_file])

        update_progress("Video conversion completed.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred during video conversion.")

def generate_m3u8():
    output_dir = output_entry.get()
    output_filename = output_filename_entry.get()
    min_br = min_bitrate_entry.get()
    max_br = max_bitrate_entry.get()
    step_br = step_bitrate_entry.get()

    try:
        min_br_int = int(min_br)
        max_br_int = int(max_br)
        step_br_int = int(step_br)

        playlist_path = f"{output_dir}/{output_filename}_hls.m3u8"
        open(playlist_path, 'w').close()  # Create/clear the playlist file

        for br in range(min_br_int, max_br_int + 1, step_br_int):
            bitrate = f"{br}k"
            segment_dir = f"{output_dir}/{output_filename}_{bitrate}"
            if not os.path.exists(segment_dir):
                continue
            update_progress(f"Segmenting: {bitrate}")
            subprocess.run(["mediafilesegmenter", "-i", f"{segment_dir}.mp4", "-B", f"seg_{bitrate}", "-f", segment_dir])

            with open(playlist_path, "a") as playlist:
                playlist.write(f"#EXT-X-STREAM-INF:BANDWIDTH={br}\n")
                playlist.write(f"{output_filename}_{bitrate}/prog_index.m3u8\n")

        update_progress("M3U8 generation completed.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred during M3U8 generation.")

def start_conversion_thread():
    threading.Thread(target=run_hls_conversion, daemon=True).start()

def start_video_conversion_thread():
    threading.Thread(target=convert_videos, daemon=True).start()

def start_m3u8_generation_thread():
    threading.Thread(target=generate_m3u8, daemon=True).start()

def run_hls_conversion():
    convert_videos()
    generate_m3u8()

app = tk.Tk()
app.title("HLS Converter")

tk.Label(app, text="Source File:").pack()
source_entry = tk.Entry(app, width=50)
source_entry.pack()
tk.Button(app, text="Browse", command=open_file_dialog).pack()

tk.Label(app, text="Output Directory:").pack()
output_entry = tk.Entry(app, width=50)
output_entry.pack()
tk.Button(app, text="Browse", command=open_directory_dialog).pack()

tk.Label(app, text="Output Filename:").pack()
output_filename_entry = tk.Entry(app, width=50)
output_filename_entry.pack()

tk.Label(app, text="Minimum Bitrate (kbps):").pack()
min_bitrate_entry = tk.Entry(app)
min_bitrate_entry.insert(0, "10000")
min_bitrate_entry.pack()

tk.Label(app, text="Maximum Bitrate (kbps):").pack()
max_bitrate_entry = tk.Entry(app)
max_bitrate_entry.insert(0, "40000")
max_bitrate_entry.pack()

tk.Label(app, text="Step Bitrate (kbps):").pack()
step_bitrate_entry = tk.Entry(app)
step_bitrate_entry.insert(0, "5000")
step_bitrate_entry.pack()

tk.Button(app, text="Just Convert Videos", command=start_video_conversion_thread).pack()
tk.Button(app, text="Just Generate the M3U8", command=start_m3u8_generation_thread).pack()
tk.Button(app, text="Full Process", command=start_conversion_thread).pack()

progress_label = tk.Label(app, text="")
progress_label.pack()

app.mainloop()