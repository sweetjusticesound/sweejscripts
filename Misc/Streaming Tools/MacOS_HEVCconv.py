import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading

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

def run_hls_conversion():
    source = source_entry.get()
    output = output_entry.get()
    min_br = min_bitrate_entry.get()
    max_br = max_bitrate_entry.get()
    step_br = step_bitrate_entry.get()

    try:
        min_br_int = int(min_br)
        max_br_int = int(max_br)
        step_br_int = int(step_br)

        # Ensure the bitrate values are valid
        if min_br_int < 10000 or max_br_int > 40000 or step_br_int <= 0:
            raise ValueError("Invalid bitrate values.")

        for br in range(min_br_int, max_br_int + 1, step_br_int):
            bitrate = f"{br}k"
            update_progress(f"Transcoding at bitrate: {bitrate}")
            subprocess.run(["ffmpeg", "-i", source, "-c:v", "hevc", "-b:v", bitrate, "-c:a", "copy", f"{output}/output_{bitrate}.mp4"])
            
            update_progress(f"Segmenting: {bitrate}")
            subprocess.run(["mediafilesegmenter", "-i", f"{output}/output_{bitrate}.mp4", "-B", f"seg_{bitrate}", "-f", f"{output}/variant_{bitrate}"])

            with open(f"{output}/playlist.m3u8", "a") as playlist:
                playlist.write(f"#EXT-X-STREAM-INF:BANDWIDTH={br}\n")
                playlist.write(f"variant_{bitrate}/prog_index.m3u8\n")

        update_progress("HLS conversion completed.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", "An error occurred during the conversion process.")

def start_conversion_thread():
    threading.Thread(target=run_hls_conversion, daemon=True).start()

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

tk.Button(app, text="Run", command=start_conversion_thread).pack()

progress_label = tk.Label(app, text="")
progress_label.pack()

app.mainloop()
