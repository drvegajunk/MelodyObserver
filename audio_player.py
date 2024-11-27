import pygame
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import wave
import threading
import time

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.is_playing = False
        self.start_time = 0
        pygame.mixer.init()
        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self.root, text="Load Audio", command=self.load_audio, width=20)
        self.load_button.pack(pady=10)
        
        self.play_button = tk.Button(self.root, text="Play", command=self.play_audio, width=20, state=tk.DISABLED)
        self.play_button.pack(pady=10)
        
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_audio, width=20, state=tk.DISABLED)
        self.pause_button.pack(pady=10)
        
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_audio, width=20, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=800, height=300, bg="white")
        self.canvas.pack(pady=20)
        
        self.timestamp_label = tk.Label(self.root, text="Timestamp: 0:00 / 0:00")
        self.timestamp_label.pack(pady=10)

    def load_audio(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if self.file_path:
            pygame.mixer.music.load(self.file_path)
            self.play_button.config(state=tk.NORMAL)
            self.plot_waveform()

    def plot_waveform(self):
        if self.file_path.endswith(".wav"):
            with wave.open(self.file_path, "rb") as wav_file:
                n_frames = wav_file.getnframes()
                framerate = wav_file.getframerate()
                duration = n_frames / float(framerate)
                self.audio_duration = duration
                audio_frames = wav_file.readframes(n_frames)
                audio_array = np.frombuffer(audio_frames, dtype=np.int16)
                n_channels = wav_file.getnchannels()
                if n_channels == 2:
                    audio_array = audio_array[::2]
                times = np.linspace(0, duration, num=n_frames)
                self.canvas.delete("all")
                fig, ax = plt.subplots(figsize=(8, 3))
                ax.plot(times, audio_array)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Amplitude")
                fig.canvas.draw()
                waveform_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
                waveform_image = waveform_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                plt.close(fig)

    def play_audio(self):
        if not self.is_playing:
            pygame.mixer.music.play()
            self.is_playing = True
            self.start_time = time.time()
            self.play_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.update_timestamp, daemon=True).start()

    def pause_audio(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.config(state=tk.NORMAL)

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.timestamp_label.config(text="Timestamp: 0:00 / 0:00")

    def update_timestamp(self):
        while self.is_playing:
            elapsed = time.time() - self.start_time
            current_time = time.strftime("%M:%S", time.gmtime(elapsed))
            total_time = time.strftime("%M:%S", time.gmtime(self.audio_duration))
            self.timestamp_label.config(text=f"Timestamp: {current_time} / {total_time}")
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio Player with Visualization")
    root.geometry("800x600")
    app = AudioPlayer(root)
    root.mainloop()