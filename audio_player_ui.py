import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import wave
from io import BytesIO
from PIL import Image, ImageTk
import threading
import time


class AudioPlayerUi:
    AUDIO_PLAYER_TITLE = "Melody Observer"
    AUDIO_PLAYER_WINDOW_WIDTH = 800
    AUDIO_PLAYER_WINDOW_HEIGHT = 600
    WAVEFORM_WINDOW_WIDTH = AUDIO_PLAYER_WINDOW_WIDTH
    WAVEFORM_WINDOW_HEIGHT = AUDIO_PLAYER_WINDOW_HEIGHT // 2
    TIMESTAMP_START_TEXT = "Timestamp: 0:00 / 0:00"

    def __init__(self):
        self.start_time = 0
        self.audio_duration = 0
        self.zoom_level = 1.0
        self.start_view = 0
        self.is_playing = False

        root = tk.Tk()
        root.title(self.AUDIO_PLAYER_TITLE)
        root.geometry(
            f"{self.AUDIO_PLAYER_WINDOW_HEIGHT}x{self.AUDIO_PLAYER_WINDOW_WIDTH}")
        self.__init_ui_elements(root)
        self.root = root

    def mainloop(self):
        self.root.mainloop()

    def load(self):
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav")])
        if not file_path:
            raise FileNotFoundError()

        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.load_audio_button.config(state=tk.DISABLED)
        self.__plot_waveform(file_path)
        return file_path

    def play(self):
        self.is_playing = True
        self.start_time = time.time()
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(
            target=self.__update_timestamp_and_cursor).start()

    def pause(self):
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)

    def stop(self):
        self.is_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.timestamp_label.config(text=self.TIMESTAMP_START_TEXT)
        self.waveform_canvas.delete(self.cursor_line)
        self.cursor_line = None

    def __init_ui_elements(self, root):
        self.load_audio_button = tk.Button(root, text="Load Audio", width=20)
        self.load_audio_button.pack(pady=10)
        self.play_button = tk.Button(
            root, text="Play", width=20, state=tk.DISABLED)
        self.play_button.pack(pady=10)
        self.pause_button = tk.Button(
            root, text="Pause", width=20, state=tk.DISABLED)
        self.pause_button.pack(pady=10)
        self.stop_button = tk.Button(
            root, text="Stop", width=20, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        self.timestamp_label = tk.Label(root, text=self.TIMESTAMP_START_TEXT)
        self.timestamp_label.pack(pady=10)
        self.waveform_canvas = tk.Canvas(
            root, width=self.WAVEFORM_WINDOW_WIDTH, height=self.WAVEFORM_WINDOW_HEIGHT, bg="white")
        self.waveform_canvas.pack(pady=20)
        self.waveform_canvas.bind("<MouseWheel>", self.__zoom_waveform)
        self.waveform_canvas.bind("<Button-4>", self.__zoom_waveform)
        self.waveform_canvas.bind("<Button-5>", self.__zoom_waveform)
        self.cursor_line = None

    def __plot_waveform(self, file_path):
        with wave.open(file_path, "rb") as wav_file:
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
            audio_array = (audio_array * (self.WAVEFORM_WINDOW_HEIGHT // 2)
                           ) + (self.WAVEFORM_WINDOW_HEIGHT // 2)
            times = np.linspace(0, len(audio_array) /
                                framerate, num=len(audio_array))

            view_duration = self.audio_duration / self.zoom_level
            end_view = min(self.start_view + view_duration,
                           self.audio_duration)
            start_idx = int(
                (self.start_view / self.audio_duration) * len(audio_array))
            end_idx = int((end_view / self.audio_duration) * len(audio_array))
            visible_times = times[start_idx:end_idx]
            visible_audio = audio_array[start_idx:end_idx]

            fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
            ax.plot(visible_times, visible_audio, color="blue", linewidth=1)
            ax.set_xlim(self.start_view, end_view)
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
            self.waveform_canvas.create_image(
                0, 0, anchor=tk.NW, image=self.waveform_image)
            plt.close(fig)

    def __zoom_waveform(self, event):
        if event.delta > 0 and self.zoom_level < 10.0:
            self.zoom_level *= 1.1
        elif event.delta < 0 and self.zoom_level > 1.0:
            self.zoom_level /= 1.1
        view_duration = self.audio_duration / self.zoom_level
        self.start_view = max(
            0, min(self.start_view, self.audio_duration - view_duration))
        self.__plot_waveform()

    def __update_timestamp_and_cursor(self):
        while self.is_playing:
            elapsed = time.time() - self.start_time
            current_time = time.strftime("%M:%S", time.gmtime(elapsed))
            total_time = time.strftime(
                "%M:%S", time.gmtime(self.audio_duration))
            self.timestamp_label.config(
                text=f"Timestamp: {current_time} / {total_time}")
            cursor_x = min(self.WAVEFORM_WINDOW_WIDTH, int(
                (elapsed / self.audio_duration) * self.WAVEFORM_WINDOW_WIDTH))
            if self.cursor_line:
                self.waveform_canvas.delete(self.cursor_line)
            self.cursor_line = self.waveform_canvas.create_line(
                cursor_x, 0, cursor_x, self.WAVEFORM_WINDOW_HEIGHT, fill="red", width=2
            )
            time.sleep(0.05)
