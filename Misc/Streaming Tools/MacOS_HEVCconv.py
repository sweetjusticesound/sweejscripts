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

def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        update_progress(f"Command Output: {result.stdout}\nCommand Error: {result.stderr}")
        return result
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

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

        if min_br_int < 10000 or max_br_int > 40000 or step_br_int <= 0 or not output_filename:
            raise ValueError("Invalid input values.")

        for br in range(min_br_int, max_br_int + 1, step_br_int):
            bitrate = f"{br}k"
            transcoded_file = f"{output_dir}/{output_filename}_{bitrate}.mp4"
            update_progress(f"Transcoding at bitrate: {bitrate}")

            scale_cmd = ["-vf", "scale=iw/2:ih/2"] if br < 15000 else []

            ffmpeg_command = ["ffmpeg", "-i", source, "-c:v", "hevc", *scale_cmd, "-b:v", bitrate, "-c:a", "copy", transcoded_file]
            run_command(ffmpeg_command)

        update_progress("Video conversion completed.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def extract_bitrate_from_filename(filename):
    # Assuming the filename format is like 'output_filename_bitrate.mp4'
    try:
        parts = filename.split('_')
        bitrate_with_extension = parts[-1]  # Get the last part which should contain the bitrate and extension
        bitrate = bitrate_with_extension.split('.')[0]  # Remove the extension
        return int(bitrate.replace('k', '')) * 1000  # Convert to bps
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract bitrate from filename: {e}")
        return None

def generate_m3u8():
    output_dir = output_entry.get()
    output_filename = output_filename_entry.get()

    try:
        playlist_path = f"{output_dir}/{output_filename}_hls.m3u8"
        open(playlist_path, 'w').close()

        # Iterate over files in the output directory and process those matching the pattern
        for file in os.listdir(output_dir):
            if file.startswith(output_filename) and file.endswith('.mp4'):
                bitrate_bps = extract_bitrate_from_filename(file)
                if bitrate_bps is None:
                    continue

                segment_file = f"{output_dir}/{file}"
                segment_dir = f"{output_dir}/{output_filename}_{bitrate_bps}k"
                update_progress(f"Segmenting: {bitrate_bps}k")

                segmenter_command = [
                    "mediafilesegmenter",
                    "-i", segment_file,
                    "-B", f"seg_{bitrate_bps}k",
                    "-f", segment_dir,
                    "-index-file", f"prog_index_{bitrate_bps}k.m3u8"
                ]

                run_command(segmenter_command)

                with open(playlist_path, "a") as playlist:
                    playlist.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate_bps}\n")
                    playlist.write(f"{output_filename}_{bitrate_bps}k/prog_index_{bitrate_bps}k.m3u8\n")

        update_progress("M3U8 generation completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during M3U8 generation: {e}")

def start_conversion_thread():
    threading.Thread(target=run_hls_conversion, daemon=True).start()

def run_hls_conversion():
    convert_videos()
    generate_m3u8()

app.mainloop()


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