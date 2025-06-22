#!/usr/bin/env python3
"""
SammyJ Batch Loudness Normaliser - Professional Audio Processing
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import os
import threading
from pathlib import Path
import soundfile as sf
import numpy as np
import pyloudnorm as pyln
import subprocess
import tempfile
from typing import List, Tuple, Optional, Dict
import traceback
import platform
from datetime import datetime


class LoudnessNormalizer:
    def __init__(self, root):
        self.root = root
        self.root.title("SammyJ Batch Loudness Normaliser")
        self.root.geometry("1200x1200")
        self.root.resizable(True, True)
        
        # Configure window style but keep close button functional
        self.root.minsize(1200, 800)  # Set minimum window size
        
        # Color scheme - Professional dark theme
        self.colors = {
            'bg_dark': '#1a1a1a',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3d3d3d',
            'accent': '#4a9eff',
            'accent_hover': '#6bb3ff',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'success': '#4caf50',
            'error': '#f44336',
            'border': '#555555'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Variables
        self.folder_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.target_loudness = tk.DoubleVar(value=-18.0)
        self.true_peak = tk.DoubleVar(value=-1.5)
        self.sample_rate = tk.IntVar(value=48000)
        self.bit_depth = tk.IntVar(value=24)
        self.is_processing = False
        
        # Limiter variables
        self.use_limiter = tk.BooleanVar(value=False)
        self.limiter_threshold = tk.DoubleVar(value=-1.0)
        self.limiter_true_peak = tk.DoubleVar(value=-0.3)
        self.limiter_makeup_gain = tk.DoubleVar(value=0.0)
        
        # Trace folder path changes
        self.folder_path.trace_add('write', self.on_folder_path_change)
        
        # Trace parameter changes for dynamic instructions
        self.target_loudness.trace_add('write', self.update_instructions)
        self.true_peak.trace_add('write', self.update_instructions)
        self.use_limiter.trace_add('write', self.on_limiter_toggle)
        self.use_limiter.trace_add('write', self.update_instructions)
        self.limiter_threshold.trace_add('write', self.update_instructions)
        self.limiter_true_peak.trace_add('write', self.update_instructions)
        self.limiter_makeup_gain.trace_add('write', self.update_instructions)
        
        # Supported formats
        self.audio_extensions = {'.wav', '.flac', '.aiff', '.aif', '.mp3', '.ogg', '.m4a'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        
        # Configure ttk styles
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure frame styles
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Medium.TFrame', background=self.colors['bg_medium'], relief='flat', borderwidth=1)
        style.configure('Title.TLabel', background=self.colors['bg_dark'], foreground=self.colors['text_primary'],
                       font=('SF Pro Display', 26, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel', background=self.colors['bg_dark'], foreground=self.colors['text_secondary'],
                       font=('SF Pro Display', 12) if platform.system() == 'Darwin' else ('Segoe UI', 11))
        
        # Configure label styles
        style.configure('Dark.TLabel', background=self.colors['bg_medium'], foreground=self.colors['text_primary'],
                       font=('SF Pro Text', 11) if platform.system() == 'Darwin' else ('Segoe UI', 10))
        
        # Configure button styles
        style.configure('Accent.TButton', font=('SF Pro Text', 12, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 11, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover']), ('!active', self.colors['accent'])],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Configure entry styles
        style.configure('Dark.TEntry', fieldbackground=self.colors['bg_light'], foreground=self.colors['text_primary'],
                       borderwidth=1, relief='flat')
        
        # Configure spinbox styles
        style.configure('Dark.TSpinbox', fieldbackground=self.colors['bg_light'], foreground=self.colors['text_primary'],
                       background=self.colors['bg_medium'], borderwidth=1, relief='flat')
        
        # Configure combobox styles
        style.configure('Dark.TCombobox', fieldbackground=self.colors['bg_light'], foreground=self.colors['text_primary'],
                       background=self.colors['bg_medium'], borderwidth=1, relief='flat')
        
        # Configure progressbar
        style.configure('Dark.Horizontal.TProgressbar', background=self.colors['accent'],
                       troughcolor=self.colors['bg_light'], borderwidth=0, lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        # Configure checkbox
        style.configure('Dark.TCheckbutton', background=self.colors['bg_medium'], foreground=self.colors['text_primary'],
                       font=('SF Pro Text', 11) if platform.system() == 'Darwin' else ('Segoe UI', 10))
        
    def setup_ui(self):
        # Main container with dark background
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title section
        title_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="SammyJ Batch Loudness Normaliser", style='Title.TLabel')
        title_label.pack()
        
        # Instructions section
        instructions_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding="15")
        instructions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        instructions_title = ttk.Label(instructions_frame, text="How to Use", 
                                     font=('SF Pro Text', 13, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'),
                                     background=self.colors['bg_medium'],
                                     foreground=self.colors['text_primary'])
        instructions_title.pack(anchor='w', pady=(0, 10))
        
        # Store instruction labels for dynamic updates
        self.instruction_labels = []
        
        instructions_text = [
            "1. Select a source folder containing audio files (WAV, FLAC, MP3, etc.) or video files (MP4, MOV, MKV, etc.)",
            "2. Choose an output folder (defaults to source folder) - files will be saved with descriptive names",
            "3. OPTIONAL: Enable limiter for initial peak control (Step 1 in processing chain)",
            "4. Set your target loudness and true peak limit for normalization (Step 2 in processing chain)",
            "5. Configure sample rate and bit depth for output files",
            "6. Click 'PROCESS FILES' to normalize all media files in the folder",
            "",
            "Processing Order: Limiter → Loudness Normalization → True Peak Limiting",
            "• Audio files are processed directly",
            "• Video files have their audio extracted, normalized, and saved as separate audio files",
            "",
            "OUTPUT_NAMING_PLACEHOLDER",  # This will be updated dynamically
            "Note: Output filename dynamically reflects your chosen settings above",
            "This prevents overwriting originals when input and output folders are the same."
        ]
        
        for i, instruction in enumerate(instructions_text):
            label = ttk.Label(instructions_frame, text=instruction,
                            font=('SF Pro Text', 10) if platform.system() == 'Darwin' else ('Segoe UI', 9),
                            background=self.colors['bg_medium'],
                            foreground=self.colors['text_secondary'])
            label.pack(anchor='w', pady=1)
            self.instruction_labels.append(label)
        
        # Update the output naming instruction
        self.update_instructions()
        
        # Folder selection section
        folder_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding="15")
        folder_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)
        
        # Input folder
        ttk.Label(folder_frame, text="Source Folder:", style='Dark.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(folder_frame, textvariable=self.folder_path, style='Dark.TEntry', width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(folder_frame, text="Browse", command=self.select_folder, style='Accent.TButton').grid(row=0, column=2)
        
        # Output folder
        ttk.Label(folder_frame, text="Output Folder:", style='Dark.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_entry = ttk.Entry(folder_frame, textvariable=self.output_path, style='Dark.TEntry', width=50, state='disabled')
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.output_button = ttk.Button(folder_frame, text="Browse", command=self.select_output_folder, style='Accent.TButton', state='disabled')
        self.output_button.grid(row=1, column=2, pady=(10, 0))
        
        # Limiter section (Step 1 in processing chain)
        limiter_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding="15")
        limiter_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Limiter title
        limiter_title = ttk.Label(limiter_frame, text="Step 1: Limiter (Optional)", 
                                 font=('SF Pro Text', 13, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'), 
                                 background=self.colors['bg_medium'], 
                                 foreground=self.colors['text_primary'])
        limiter_title.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        # Limiter checkbox
        self.limiter_check = ttk.Checkbutton(limiter_frame, text="Enable Limiter", 
                                            variable=self.use_limiter,
                                            style='Dark.TCheckbutton')
        self.limiter_check.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Limiter parameters
        ttk.Label(limiter_frame, text="Limiter Threshold (dBFS):", style='Dark.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.limiter_threshold_spin = ttk.Spinbox(limiter_frame, from_=-10, to=0, increment=0.1,
                                                 textvariable=self.limiter_threshold, width=12, 
                                                 style='Dark.TSpinbox', state='disabled')
        self.limiter_threshold_spin.grid(row=2, column=1, sticky=tk.W, padx=(10, 30), pady=5)
        
        ttk.Label(limiter_frame, text="Limiter True Peak (dBFS):", style='Dark.TLabel').grid(row=2, column=2, sticky=tk.W, pady=5)
        self.limiter_peak_spin = ttk.Spinbox(limiter_frame, from_=-3, to=0, increment=0.1,
                                            textvariable=self.limiter_true_peak, width=12,
                                            style='Dark.TSpinbox', state='disabled')
        self.limiter_peak_spin.grid(row=2, column=3, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(limiter_frame, text="Makeup Gain (dB):", style='Dark.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.makeup_gain_spin = ttk.Spinbox(limiter_frame, from_=-10, to=10, increment=0.1,
                                           textvariable=self.limiter_makeup_gain, width=12,
                                           style='Dark.TSpinbox', state='disabled')
        self.makeup_gain_spin.grid(row=3, column=1, sticky=tk.W, padx=(10, 30), pady=5)
        
        # Parameters frame (Step 2 in processing chain)
        params_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding="15")
        params_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Parameters title
        param_title = ttk.Label(params_frame, text="Step 2: Loudness Normalization", 
                               font=('SF Pro Text', 13, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'), 
                               background=self.colors['bg_medium'], 
                               foreground=self.colors['text_primary'])
        param_title.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        
        # Left side parameters
        ttk.Label(params_frame, text="Target Loudness (LKFS):", style='Dark.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        loudness_spin = ttk.Spinbox(params_frame, from_=-30, to=-10, increment=0.5, 
                                   textvariable=self.target_loudness, width=12, style='Dark.TSpinbox')
        loudness_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 30), pady=5)
        
        ttk.Label(params_frame, text="True Peak (dBFS):", style='Dark.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.peak_spin = ttk.Spinbox(params_frame, from_=-10, to=0, increment=0.1, 
                               textvariable=self.true_peak, width=12, style='Dark.TSpinbox')
        self.peak_spin.grid(row=2, column=1, sticky=tk.W, padx=(10, 30), pady=5)
        
        # Right side parameters
        ttk.Label(params_frame, text="Sample Rate:", style='Dark.TLabel').grid(row=1, column=2, sticky=tk.W, pady=5)
        sample_combo = ttk.Combobox(params_frame, textvariable=self.sample_rate, 
                                   values=[44100, 48000, 88200, 96000, 192000], width=12, style='Dark.TCombobox')
        sample_combo.grid(row=1, column=3, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Bit Depth:", style='Dark.TLabel').grid(row=2, column=2, sticky=tk.W, pady=5)
        depth_combo = ttk.Combobox(params_frame, textvariable=self.bit_depth, 
                                  values=[16, 24, 32], width=12, style='Dark.TCombobox')
        depth_combo.grid(row=2, column=3, sticky=tk.W, padx=10, pady=5)
        
        # Process button
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.grid(row=5, column=0, pady=(0, 15))
        
        self.process_btn = ttk.Button(button_frame, text="PROCESS FILES", command=self.start_processing, 
                                     style='Accent.TButton', width=20)
        self.process_btn.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', style='Dark.Horizontal.TProgressbar')
        self.progress.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Results section
        results_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding="15")
        results_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        results_title = ttk.Label(results_frame, text="Processing Results", 
                                 font=('SF Pro Text', 13, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 12, 'bold'),
                                 background=self.colors['bg_medium'],
                                 foreground=self.colors['text_primary'])
        results_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create text widget with custom styling
        text_frame = tk.Frame(results_frame, bg=self.colors['bg_light'], highlightbackground=self.colors['border'], 
                             highlightthickness=1)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, 
                                   bg=self.colors['bg_light'], 
                                   fg=self.colors['text_primary'],
                                   font=('SF Mono', 11) if platform.system() == 'Darwin' else ('Consolas', 10),
                                   insertbackground=self.colors['text_primary'],
                                   selectbackground=self.colors['accent'],
                                   selectforeground=self.colors['text_primary'],
                                   wrap=tk.WORD,
                                   bd=0)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Configure grid weights for expansion
        main_frame.rowconfigure(7, weight=1)
        
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)
            
    def on_folder_path_change(self, *args):
        if self.folder_path.get():
            # Enable output folder controls
            self.output_entry.config(state='normal')
            self.output_button.config(state='normal')
            # Set output path to same as input path by default
            self.output_path.set(self.folder_path.get())
        else:
            # Disable output folder controls
            self.output_entry.config(state='disabled')
            self.output_button.config(state='disabled')
            self.output_path.set('')
            
    def update_instructions(self, *args):
        # Update the output naming instruction (index 10)
        if hasattr(self, 'instruction_labels') and len(self.instruction_labels) > 10:
            try:
                loudness_str = f"{abs(int(self.target_loudness.get()))}lkfs"
                
                if self.use_limiter.get():
                    # Use limiter true peak value
                    peak_str = f"tp{abs(self.limiter_true_peak.get()):.1f}dbfs".replace('.', '_')
                    threshold_str = f"_lim{abs(self.limiter_threshold.get()):.1f}db".replace('.', '_')
                    naming_text = f"Output naming: filename_normalized_{loudness_str}_{peak_str}{threshold_str}_timestamp.ext"
                else:
                    # Use regular true peak value
                    peak_str = f"tp{abs(self.true_peak.get()):.1f}dbfs".replace('.', '_')
                    naming_text = f"Output naming: filename_normalized_{loudness_str}_{peak_str}_timestamp.ext"
                
                self.instruction_labels[10].config(text=naming_text)
                # Make it stand out
                self.instruction_labels[10].config(foreground=self.colors['accent'])
            except:
                pass  # Handle initial setup when values aren't set yet
                
    def on_limiter_toggle(self, *args):
        if self.use_limiter.get():
            # Enable limiter controls, keep normalization true peak active
            self.limiter_threshold_spin.config(state='normal')
            self.limiter_peak_spin.config(state='normal')
            self.makeup_gain_spin.config(state='normal')
            # Both limiter and normalization true peak remain active
        else:
            # Disable limiter controls only
            self.limiter_threshold_spin.config(state='disabled')
            self.limiter_peak_spin.config(state='disabled')
            self.makeup_gain_spin.config(state='disabled')
            
    def start_processing(self):
        if not self.folder_path.get():
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
            
        if self.is_processing:
            return
            
        self.is_processing = True
        self.process_btn.config(state='disabled')
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
        
    def process_files(self):
        try:
            folder = Path(self.folder_path.get())
            
            # Find all audio and video files
            audio_files = []
            video_files = []
            
            for file in folder.iterdir():
                if file.is_file():
                    ext = file.suffix.lower()
                    if ext in self.audio_extensions:
                        audio_files.append(file)
                    elif ext in self.video_extensions:
                        video_files.append(file)
            
            self.log(f"Found {len(audio_files)} audio files and {len(video_files)} video files\n", 'accent')
            
            # Process audio files
            for file in audio_files:
                self.process_audio_file(file)
                
            # Process video files
            for file in video_files:
                self.process_video_file(file)
                
        except Exception as e:
            self.log(f"Error during processing: {str(e)}\n{traceback.format_exc()}")
        finally:
            self.root.after(0, self.processing_complete)
            
    def processing_complete(self):
        self.progress.stop()
        self.process_btn.config(state='normal')
        self.is_processing = False
        self.log("\n✓ Processing complete!\n", 'success')
        
    def log(self, message, color=None):
        def _log():
            # Insert with color tag if specified
            if color:
                start_index = self.results_text.index(tk.END)
                self.results_text.insert(tk.END, message)
                end_index = self.results_text.index(tk.END)
                self.results_text.tag_add(color, start_index, end_index)
                self.results_text.tag_config(color, foreground=self.colors.get(color, self.colors['text_primary']))
            else:
                self.results_text.insert(tk.END, message)
            self.results_text.see(tk.END)
        self.root.after(0, _log)
        
    def measure_loudness(self, audio: np.ndarray, rate: int) -> Tuple[float, float]:
        """Measure integrated loudness and true peak"""
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(audio)
        
        # Calculate true peak
        if len(audio.shape) == 1:
            true_peak_db = 20 * np.log10(np.max(np.abs(audio)) + 1e-10)
        else:
            true_peak_db = 20 * np.log10(np.max(np.abs(audio)) + 1e-10)
            
        return loudness, true_peak_db
        
    def process_audio_file(self, file_path: Path):
        try:
            self.log(f"\nProcessing: {file_path.name}")
            
            # Read audio file
            audio, rate = sf.read(str(file_path))
            
            # Ensure audio is float64 for pyloudnorm
            audio = audio.astype(np.float64)
            
            # Measure original loudness
            original_loudness, original_peak = self.measure_loudness(audio, rate)
            self.log(f"  Original: {original_loudness:.1f} LKFS, Peak: {original_peak:.1f} dBFS")
            
            # Step 1: Apply limiter first (if enabled)
            processed_audio = audio.copy()
            if self.use_limiter.get():
                self.log(f"  Applying limiter (threshold: {self.limiter_threshold.get():.1f} dBFS)")
                threshold = 10 ** (self.limiter_threshold.get() / 20)
                peak_limit = 10 ** (self.limiter_true_peak.get() / 20)
                
                # Simple soft-knee limiter
                for i in range(len(processed_audio)):
                    if len(processed_audio.shape) == 1:
                        # Mono
                        if abs(processed_audio[i]) > threshold:
                            # Apply soft knee compression above threshold
                            ratio = 10.0  # 10:1 ratio
                            excess = abs(processed_audio[i]) - threshold
                            compressed_excess = excess / ratio
                            new_value = threshold + compressed_excess
                            processed_audio[i] = new_value * np.sign(processed_audio[i])
                    else:
                        # Stereo/multichannel
                        for ch in range(processed_audio.shape[1]):
                            if abs(processed_audio[i, ch]) > threshold:
                                excess = abs(processed_audio[i, ch]) - threshold
                                compressed_excess = excess / ratio
                                new_value = threshold + compressed_excess
                                processed_audio[i, ch] = new_value * np.sign(processed_audio[i, ch])
                
                # Apply makeup gain
                makeup_gain_linear = 10 ** (self.limiter_makeup_gain.get() / 20)
                processed_audio = processed_audio * makeup_gain_linear
                
                # Apply limiter true peak limiting (after makeup gain)
                max_peak = np.max(np.abs(processed_audio))
                if max_peak > peak_limit:
                    processed_audio = processed_audio * (peak_limit / max_peak)
                
                # Measure post-limiter levels
                post_limiter_loudness, post_limiter_peak = self.measure_loudness(processed_audio, rate)
                self.log(f"  Post-limiter: {post_limiter_loudness:.1f} LKFS, Peak: {post_limiter_peak:.1f} dBFS")
            
            # Step 2: Apply loudness normalization
            meter = pyln.Meter(rate)
            current_loudness, _ = self.measure_loudness(processed_audio, rate)
            normalized_audio = pyln.normalize.loudness(processed_audio, current_loudness, 
                                                      self.target_loudness.get())
            
            # Apply normalization true peak limiting
            peak_limit = 10 ** (self.true_peak.get() / 20)
            max_peak = np.max(np.abs(normalized_audio))
            if max_peak > peak_limit:
                normalized_audio = normalized_audio * (peak_limit / max_peak)
            
            # Measure new loudness
            new_loudness, new_peak = self.measure_loudness(normalized_audio, rate)
            self.log(f"  Normalized: {new_loudness:.1f} LKFS, Peak: {new_peak:.1f} dBFS")
            
            # Resample if necessary
            target_rate = self.sample_rate.get()
            if rate != target_rate:
                import resampy
                normalized_audio = resampy.resample(normalized_audio, rate, target_rate, axis=0)
                self.log(f"  Resampled: {rate} Hz → {target_rate} Hz")
            
            # Convert bit depth
            bit_depth = self.bit_depth.get()
            if bit_depth == 16:
                subtype = 'PCM_16'
            elif bit_depth == 24:
                subtype = 'PCM_24'
            else:
                subtype = 'PCM_32'
            
            # Generate output filename with stats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            loudness_str = f"{abs(int(self.target_loudness.get()))}lkfs"
            
            if self.use_limiter.get():
                peak_str = f"tp{abs(self.limiter_true_peak.get()):.1f}dbfs".replace('.', '_')
                threshold_str = f"_lim{abs(self.limiter_threshold.get()):.1f}db".replace('.', '_')
                output_filename = f"{file_path.stem}_normalized_{loudness_str}_{peak_str}{threshold_str}_{timestamp}{file_path.suffix}"
            else:
                peak_str = f"tp{abs(self.true_peak.get()):.1f}dbfs".replace('.', '_')
                output_filename = f"{file_path.stem}_normalized_{loudness_str}_{peak_str}_{timestamp}{file_path.suffix}"
            
            # Determine output directory
            output_dir = Path(self.output_path.get()) if self.output_path.get() else file_path.parent
            output_path = output_dir / output_filename
            
            # Save normalized file
            sf.write(str(output_path), normalized_audio, target_rate, subtype=subtype)
            self.log(f"  ✓ Saved: {output_path.name}\n", 'success')
            
        except Exception as e:
            self.log(f"  ✗ ERROR: {str(e)}\n", 'error')
            messagebox.showerror("Processing Error", f"Error processing {file_path.name}:\n{str(e)}")
            
    def process_video_file(self, file_path: Path):
        try:
            self.log(f"\nProcessing video: {file_path.name}")
            
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg', '-i', str(file_path),
                '-vn',  # No video
                '-acodec', 'pcm_s24le',  # 24-bit PCM
                '-ar', str(self.sample_rate.get()),  # Sample rate
                '-y',  # Overwrite
                tmp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
                
            # Process the extracted audio
            self.process_audio_file(Path(tmp_path))
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            self.log(f"  ✗ ERROR extracting audio: {str(e)}\n", 'error')
            messagebox.showerror("Video Processing Error", 
                               f"Failed to extract audio from {file_path.name}:\n{str(e)}\n\nContinuing with other files...")


def main():
    root = tk.Tk()
    app = LoudnessNormalizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()