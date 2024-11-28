import pygame
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import wave
import threading
import time
from io import BytesIO
from PIL import Image, ImageTk


class AudioPlayer:
    WAVEFORM_WINDOW_WIDTH = 800
    WAVEFORM_WINDOW_HEIGHT = 300

    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.is_playing = False
        self.start_time = 0
        self.audio_duration = 0
        pygame.init()
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
        self.timestamp_label = tk.Label(self.root, text="Timestamp: 0:00 / 0:00")
        self.timestamp_label.pack(pady=10)
        self.waveform_canvas = tk.Canvas(self.root, width=self.WAVEFORM_WINDOW_WIDTH, height=self.WAVEFORM_WINDOW_HEIGHT, bg="white")
        self.waveform_canvas.pack(pady=20)
        self.cursor_line = None

    def load_audio(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if self.file_path:
            pygame.mixer.music.load(self.file_path)
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.DISABLED)
            self.plot_waveform()

    def plot_waveform(self):
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

            audio_array = audio_array / np.max(np.abs(audio_array))
            audio_array = (audio_array * (self.WAVEFORM_WINDOW_HEIGHT // 2)) + (self.WAVEFORM_WINDOW_HEIGHT // 2)
            times = np.linspace(0, self.WAVEFORM_WINDOW_WIDTH, num=len(audio_array))

            fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
            ax.plot(times, audio_array, color="blue", linewidth=1)
            ax.set_xlim(0, self.WAVEFORM_WINDOW_WIDTH)
            ax.set_ylim(0, self.WAVEFORM_WINDOW_HEIGHT)
            ax.axis("off")
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            buf = BytesIO()
            fig.savefig(buf, format="PNG", dpi=100)
            buf.seek(0)
            image_data = buf.read()
            buf.close()
            image = Image.open(BytesIO(image_data))
            self.waveform_image = ImageTk.PhotoImage(image)
            self.waveform_canvas.create_image(0, 0, anchor=tk.NW, image=self.waveform_image)
            plt.close(fig)

    def play_audio(self):
        if not self.is_playing:
            pygame.mixer.music.play()
            self.is_playing = True
            self.start_time = time.time()
            self.play_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.update_timestamp_and_cursor, daemon=True).start()

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
        self.waveform_canvas.delete(self.cursor_line)
        self.cursor_line = None

    def update_timestamp_and_cursor(self):
        while self.is_playing:
            elapsed = time.time() - self.start_time
            current_time = time.strftime("%M:%S", time.gmtime(elapsed))
            total_time = time.strftime("%M:%S", time.gmtime(self.audio_duration))
            self.timestamp_label.config(text=f"Timestamp: {current_time} / {total_time}")
            cursor_x = min(self.WAVEFORM_WINDOW_WIDTH, int((elapsed / self.audio_duration) * self.WAVEFORM_WINDOW_WIDTH))
            if self.cursor_line:
                self.waveform_canvas.delete(self.cursor_line)
            self.cursor_line = self.waveform_canvas.create_line(
                cursor_x, 0, cursor_x, self.WAVEFORM_WINDOW_HEIGHT, fill="red", width=2
            )
            time.sleep(0.05)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio Player with Waveform Visualization")
    root.geometry("800x600")
    app = AudioPlayer(root)
    root.mainloop()
