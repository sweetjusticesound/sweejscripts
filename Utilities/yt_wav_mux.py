#!/usr/bin/env python3
"""
yt_wav_mux — download a YouTube video at highest quality, replace its audio
with a local WAV (optionally trimming a 2-second 2-pop from the head), and
mux to MP4 with high-quality AAC.

Requires: yt-dlp and ffmpeg on PATH.
Uses Apple AudioToolbox AAC (aac_at) when available, falling back to
ffmpeg's native encoder at 320k.
"""

import os
import re
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def which_or_die(name):
    path = shutil.which(name)
    if not path:
        messagebox.showerror("Missing dependency", f"'{name}' not found on PATH.")
        raise SystemExit(1)
    return path


def aac_encoder(ffmpeg):
    """Prefer Apple AudioToolbox AAC if this ffmpeg build has it."""
    try:
        out = subprocess.run(
            [ffmpeg, "-hide_banner", "-encoders"],
            capture_output=True, text=True
        ).stdout
        if " aac_at " in out:
            return ["-c:a", "aac_at", "-b:a", "320k"]
    except Exception:
        pass
    return ["-c:a", "aac", "-b:a", "320k"]


class MuxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT + WAV Muxer")
        self.resizable(True, False)
        self.minsize(560, 0)

        self.ytdlp = which_or_die("yt-dlp")
        self.ffmpeg = which_or_die("ffmpeg")

        self.url = tk.StringVar()
        self.wav = tk.StringVar()
        self.out = tk.StringVar()
        self.trim_pop = tk.BooleanVar(value=False)
        self.prefer_h264 = tk.BooleanVar(value=False)
        self.grab_thumb = tk.BooleanVar(value=False)
        self._out_user_edited = False
        self._running = False

        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(self, padding=8)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="YouTube URL").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.url).grid(row=0, column=1, columnspan=2, sticky="ew", **pad)

        ttk.Label(frm, text="WAV file").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.wav).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Browse…", command=self.pick_wav).grid(row=1, column=2, **pad)

        ttk.Label(frm, text="Output file").grid(row=2, column=0, sticky="w", **pad)
        out_entry = ttk.Entry(frm, textvariable=self.out)
        out_entry.grid(row=2, column=1, sticky="ew", **pad)
        out_entry.bind("<Key>", lambda e: setattr(self, "_out_user_edited", True))
        ttk.Button(frm, text="Save as…", command=self.pick_out).grid(row=2, column=2, **pad)

        ttk.Checkbutton(
            frm, text="Trim 2-pop (remove first 2 s of WAV)", variable=self.trim_pop
        ).grid(row=3, column=1, sticky="w", **pad)
        ttk.Checkbutton(
            frm, text="Prefer H.264 (QuickTime-safe; may cap resolution)",
            variable=self.prefer_h264
        ).grid(row=4, column=1, sticky="w", **pad)
        ttk.Checkbutton(
            frm, text="Save thumbnail as PNG (alongside output)",
            variable=self.grab_thumb
        ).grid(row=5, column=1, sticky="w", **pad)

        self.go_btn = ttk.Button(frm, text="Download && Mux", command=self.start)
        self.go_btn.grid(row=6, column=1, sticky="e", **pad)

        self.status = tk.StringVar(value="Ready.")
        ttk.Label(frm, textvariable=self.status, anchor="w").grid(
            row=7, column=0, columnspan=3, sticky="ew", **pad
        )

        self.log = tk.Text(frm, height=12, width=80, state="disabled", wrap="none")
        self.log.grid(row=8, column=0, columnspan=3, sticky="nsew", **pad)

    # ---------- UI helpers ----------

    def pick_wav(self):
        path = filedialog.askopenfilename(
            title="Select WAV", filetypes=[("WAV files", "*.wav *.WAV"), ("All files", "*")]
        )
        if path:
            self.wav.set(path)
            if not self._out_user_edited:
                base = os.path.splitext(os.path.basename(path))[0]
                self.out.set(os.path.join(os.path.dirname(path), f"{base}_mux.mp4"))

    def pick_out(self):
        initial = self.out.get()
        path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".mp4",
            initialdir=os.path.dirname(initial) if initial else None,
            initialfile=os.path.basename(initial) if initial else None,
            filetypes=[("MP4", "*.mp4"), ("All files", "*")],
        )
        if path:
            self.out.set(path)
            self._out_user_edited = True

    def log_line(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_status(self, text):
        self.status.set(text)

    # ---------- pipeline ----------

    def start(self):
        if self._running:
            return
        url, wav, out = self.url.get().strip(), self.wav.get().strip(), self.out.get().strip()
        if not url:
            messagebox.showwarning("Missing input", "Enter a YouTube URL.")
            return
        if not wav or not os.path.isfile(wav):
            messagebox.showwarning("Missing input", "Select a valid WAV file.")
            return
        if not out:
            messagebox.showwarning("Missing input", "Set an output path.")
            return
        if os.path.exists(out) and not messagebox.askyesno(
            "Overwrite?", f"{out}\nalready exists. Overwrite?"
        ):
            return
        self._running = True
        self.go_btn.configure(state="disabled")
        threading.Thread(target=self.run_pipeline, args=(url, wav, out), daemon=True).start()

    def run_proc(self, cmd):
        self.log_line("$ " + " ".join(cmd))
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        for line in proc.stdout:
            # keep yt-dlp progress lines readable without flooding
            line = line.rstrip()
            if line:
                self.after(0, self.log_line, line)
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"{os.path.basename(cmd[0])} exited {proc.returncode}")

    def run_pipeline(self, url, wav, out):
        tmpdir = tempfile.mkdtemp(prefix="ytmux_")
        try:
            # 1) Download best video-only stream (we discard YT audio anyway)
            self.after(0, self.set_status, "Downloading video…")
            if self.prefer_h264.get():
                fmt = "bv*[vcodec^=avc]/bv*[ext=mp4]/bv*"
            else:
                fmt = "bv*/b"
            vid_tmpl = os.path.join(tmpdir, "video.%(ext)s")
            dl_cmd = [
                self.ytdlp, "-f", fmt, "--no-playlist",
                "-o", vid_tmpl,
            ]
            if self.grab_thumb.get():
                dl_cmd += ["--write-thumbnail", "--convert-thumbnails", "png"]
            dl_cmd.append(url)
            self.run_proc(dl_cmd)
            files = os.listdir(tmpdir)
            vids = [f for f in files if f.startswith("video.") and not f.endswith(".png")]
            if not vids:
                raise RuntimeError("Download produced no video file.")
            video_path = os.path.join(tmpdir, vids[0])

            if self.grab_thumb.get():
                thumbs = [f for f in files if f.endswith(".png")]
                if thumbs:
                    thumb_out = os.path.splitext(out)[0] + ".png"
                    shutil.copy2(os.path.join(tmpdir, thumbs[0]), thumb_out)
                    self.after(0, self.log_line, f"Thumbnail saved: {thumb_out}")
                else:
                    self.after(0, self.log_line, "No thumbnail found for this video.")

            # 2) Mux: video stream copied, WAV -> AAC, original audio dropped
            self.after(0, self.set_status, "Muxing…")
            cmd = [self.ffmpeg, "-hide_banner", "-y"]
            cmd += ["-i", video_path]
            if self.trim_pop.get():
                cmd += ["-ss", "2", "-i", wav]
            else:
                cmd += ["-i", wav]
            cmd += [
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy",
                *aac_encoder(self.ffmpeg),
                "-movflags", "+faststart",
                "-shortest",
                out,
            ]
            self.run_proc(cmd)

            self.after(0, self.set_status, f"Done: {out}")
            self.after(0, messagebox.showinfo, "Done", f"Written:\n{out}")
        except Exception as e:
            self.after(0, self.set_status, f"Failed: {e}")
            self.after(0, messagebox.showerror, "Error", str(e))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
            self._running = False
            self.after(0, lambda: self.go_btn.configure(state="normal"))


if __name__ == "__main__":
    MuxApp().mainloop()
