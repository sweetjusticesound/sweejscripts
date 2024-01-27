import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def open_file_dialog():
    filename = filedialog.askopenfilename()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, filename)

def open_directory_dialog():
    directory = filedialog.askdirectory()
    output_entry.delete(0, tk.END)
    output_entry.insert(0, directory)

def open_audio_file_dialog():
    audio_filename = filedialog.askopenfilename()
    audio_entry.delete(0, tk.END)
    audio_entry.insert(0, audio_filename)

def update_progress(message):
    progress_label.config(text=message)
    app.update()

def run_command(command):
    try:
        subprocess.run(command)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def convert_videos():
    source = source_entry.get()
    audio_source = audio_entry.get()
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
            audio_cmd = ["-i", audio_source, "-c:a", "copy"] if audio_source else ["-c:a", "copy"]
            ffmpeg_command = [
                "ffmpeg", "-i", source, 
                *audio_cmd,
                "-c:v", "hevc", "-tag:v", "hvc1", 
                *scale_cmd, 
                "-b:v", bitrate, 
                transcoded_file
            ]

            run_command(ffmpeg_command)

        update_progress("Video conversion completed.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def extract_bitrate_from_filename(filename):
    try:
        parts = filename.split('_')
        bitrate_with_extension = parts[-1] 
        bitrate = bitrate_with_extension.split('.')[0]
        return int(bitrate.replace('k', '')) * 1000
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract bitrate from filename: {e}")
        return None

def generate_m3u8():
    output_dir = output_entry.get()
    output_filename = output_filename_entry.get()
    segment_length = segment_length_entry.get()

    try:
        segment_length_int = int(segment_length) if segment_length else 10
        variant_plists = []

        for file in os.listdir(output_dir):
            if file.startswith(output_filename) and file.endswith('.mp4'):
                bitrate_bps = extract_bitrate_from_filename(file)
                if bitrate_bps is None:
                    continue

                segment_file = f"{output_dir}/{file}"
                segment_dir = f"{output_dir}/{output_filename}_{bitrate_bps}k"
                variant_plist = f"{segment_dir}/variant_{bitrate_bps}.plist"
                variant_plists.append(variant_plist)
                update_progress(f"Segmenting: {bitrate_bps}k")

                segmenter_command = [
                    "mediafilesegmenter",
                    "--target-duration", str(segment_length_int),
                    "-f", segment_dir,
                    "-B", f"seg_{bitrate_bps}k",
                    segment_file
                ]

                run_command(segmenter_command, console_output)

        master_playlist_path = f"{output_dir}/{output_filename}_master.m3u8"
        variant_creator_command = ["variantplaylistcreator", "-o", master_playlist_path] + variant_plists
        run_command(variant_creator_command, console_output)

        update_progress("Master M3U8 generation completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during M3U8 generation: {e}")

# GUI setup
app = tk.Tk()
app.title("HLS Converter")

# Grid layout configuration
app.columnconfigure(1, weight=1)

# Audio File Selection
tk.Label(app, text="Select Dolby Atmos MP4 File (optional, will use Source Video File's audio track if left blank):").grid(row=0, column=0, columnspan=2, sticky='w')
audio_entry = tk.Entry(app, width=50)
audio_entry.grid(row=1, column=0, sticky='ew')
tk.Button(app, text="Browse", command=open_audio_file_dialog).grid(row=1, column=1)

# Source Video File Selection
tk.Label(app, text="Source Video File:").grid(row=2, column=0, columnspan=2, sticky='w')
source_entry = tk.Entry(app, width=50)
source_entry.grid(row=3, column=0, sticky='ew')
tk.Button(app, text="Browse", command=open_file_dialog).grid(row=3, column=1)

# Output Directory Selection
tk.Label(app, text="Output Directory:").grid(row=4, column=0, columnspan=2, sticky='w')
output_entry = tk.Entry(app, width=50)
output_entry.grid(row=5, column=0, sticky='ew')
tk.Button(app, text="Browse", command=open_directory_dialog).grid(row=5, column=1)

# Output Filename, Bitrate, and Segment Length
tk.Label(app, text="Output Filename:").grid(row=6, column=0, sticky='w')
output_filename_entry = tk.Entry(app, width=50)
output_filename_entry.grid(row=7, column=0, sticky='ew')

tk.Label(app, text="Minimum Bitrate (kbps):").grid(row=8, column=0, sticky='w')
min_bitrate_entry = tk.Entry(app)
min_bitrate_entry.insert(0, "10000")
min_bitrate_entry.grid(row=9, column=0, sticky='ew')

tk.Label(app, text="Maximum Bitrate (kbps):").grid(row=10, column=0, sticky='w')
max_bitrate_entry = tk.Entry(app)
max_bitrate_entry.insert(0, "40000")
max_bitrate_entry.grid(row=11, column=0, sticky='ew')

tk.Label(app, text="Step Bitrate (kbps):").grid(row=12, column=0, sticky='w')
step_bitrate_entry = tk.Entry(app)
step_bitrate_entry.insert(0, "5000")
step_bitrate_entry.grid(row=13, column=0, sticky='ew')

tk.Label(app, text="Segment Length (seconds):").grid(row=14, column=0, sticky='w')
segment_length_entry = tk.Entry(app)
segment_length_entry.insert(0, "10")  # Default segment length
segment_length_entry.grid(row=15, column=0, sticky='ew')

# Progress Label
progress_label = tk.Label(app, text="")
progress_label.grid(row=18, column=0, columnspan=2, sticky='w')

# Control Buttons
tk.Button(app, text="Just Convert Videos", command=convert_videos).grid(row=16, column=0, sticky='ew')
tk.Button(app, text="Just Generate the M3U8", command=generate_m3u8).grid(row=16, column=1, sticky='ew')
tk.Button(app, text="Full Process", command=lambda: [convert_videos(), generate_m3u8()]).grid(row=17, column=0, columnspan=2, sticky='ew')

app.mainloop()