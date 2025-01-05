import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import threading

def download_and_convert():
    url = url_entry.get()
    cookies_path = cookies_entry.get()
    format_choice = format_var.get()
    delete_original = delete_var.get()
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    if not url:
        messagebox.showerror("Error", "Please enter a video URL")
        return

    def run_download():
        try:
            # Construct the download command
            download_command = f'yt-dlp -o "{downloads_path}/%(title)s.%(ext)s"'

            # Add cookies file path if provided
            if cookies_path:
                download_command += f' --cookies "{cookies_path}"'

            download_command += f' {url}'

            process = subprocess.Popen(download_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())  # or update this to reflect in the GUI

            # Post-download processing
            convert_downloaded_video()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convert_downloaded_video():
        try:
            for file in os.listdir(downloads_path):
                if file.endswith(('.mp4', '.webm')):
                    input_file = os.path.join(downloads_path, file)
                    output_file = os.path.splitext(input_file)[0] + f'.{format_choice}'

                    # Convert to WAV 48kHz 24-bit if selected
                    if format_choice == 'wav':
                        convert_command = f'ffmpeg -i "{input_file}" -ar 48000 -acodec pcm_s24le "{output_file}"'

                    # Convert to highest quality FLAC if selected
                    elif format_choice == 'flac':
                        convert_command = f'ffmpeg -i "{input_file}" -q:a 0 "{output_file}"'

                    subprocess.run(convert_command, shell=True, check=True)

                    # Remove the original video file if checkbox is checked
                    if delete_original:
                        os.remove(input_file)

            messagebox.showinfo("Success", f"Video downloaded and converted to {format_choice.upper()} successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run_download).start()

def browse_cookies_file():
    file_path = filedialog.askopenfilename(title="Select Cookies File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        cookies_entry.delete(0, tk.END)
        cookies_entry.insert(0, file_path)

# Set up the Tkinter window
window = tk.Tk()
window.title("SammyJ's WebVid Downloader and Converter")

# URL entry
url_label = ttk.Label(window, text="Video URL:")
url_label.pack()
url_entry = ttk.Entry(window, width=50)
url_entry.pack()

# Cookies file entry
cookies_label = ttk.Label(window, text="Path to Cookies File (optional) use Chrome Extension 'get cookies TXT Locally'':")
cookies_label.pack()
cookies_frame = ttk.Frame(window)
cookies_frame.pack()
cookies_entry = ttk.Entry(cookies_frame, width=40)
cookies_entry.pack(side=tk.LEFT)
browse_button = ttk.Button(cookies_frame, text="Browse", command=browse_cookies_file)
browse_button.pack(side=tk.LEFT)

# Format dropdown
format_label = ttk.Label(window, text="Select File Format:")
format_label.pack()
format_var = tk.StringVar()
format_dropdown = ttk.Combobox(window, textvariable=format_var, state="readonly")
format_dropdown['values'] = ('wav', 'flac')
format_dropdown.pack()

# Checkbox for deleting the original video
delete_var = tk.BooleanVar(value=True)  # Checkbox is checked by default
delete_checkbox = ttk.Checkbutton(window, text="Delete original video after conversion", variable=delete_var)
delete_checkbox.pack()

# Download button
download_button = ttk.Button(window, text="Download and Convert", command=download_and_convert)
download_button.pack()

# Run the Tkinter loop
window.mainloop()
