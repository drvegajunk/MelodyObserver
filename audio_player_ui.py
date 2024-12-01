import tkinter as tk
from tkinter import filedialog
import time
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk
import numpy as np


class AudioPlayerUi:
    AUDIO_PLAYER_TITLE = "Melody Observer"
    TIMESTAMP_START_TEXT = "Timestamp: 0:00 / 0:00"
    AUDIO_PLAYER_WINDOW_HEIGHT = 800
    AUDIO_PLAYER_WINDOW_WIDTH = 600
    SIGNAL_WINDOW_WIDTH = AUDIO_PLAYER_WINDOW_WIDTH
    SIGNAL_WINDOW_HEIGHT = AUDIO_PLAYER_WINDOW_HEIGHT // 2
    SIGNAL_PLOT_DPI = 100
    SIGNAL_WIDTH_INCHES = SIGNAL_WINDOW_WIDTH // SIGNAL_PLOT_DPI
    SIGNAL_HEIGHT_INCHES = SIGNAL_WINDOW_HEIGHT // SIGNAL_PLOT_DPI
    MAX_SIGNAL_SAMPLES = 1000

    @classmethod
    def create_root(cls):
        root = tk.Tk()
        root.title(cls.AUDIO_PLAYER_TITLE)
        root.geometry(
            f"{cls.AUDIO_PLAYER_WINDOW_WIDTH}x{cls.AUDIO_PLAYER_WINDOW_HEIGHT}")
        return root

    @classmethod
    def create_timestamp_label(cls, root):
        timestamp_label = tk.Label(root, text=cls.TIMESTAMP_START_TEXT)
        timestamp_label.pack(pady=10)
        return timestamp_label

    @classmethod
    def create_signal_canvas(cls, root, callback):
        signal_canvas = tk.Canvas(
            root, width=cls.SIGNAL_WINDOW_WIDTH, height=cls.SIGNAL_WINDOW_HEIGHT, bg="white")
        signal_canvas.pack(pady=20)
        signal_canvas.bind("<MouseWheel>", callback)
        signal_canvas.bind("<Button-4>", callback)
        signal_canvas.bind("<Button-5>", callback)
        return signal_canvas

    @staticmethod
    def create_load_audio_button(root):
        load_audio_button = tk.Button(root, text="Load Audio", width=20)
        load_audio_button.pack(pady=10)
        return load_audio_button

    @staticmethod
    def create_play_button(root):
        play_button = tk.Button(root, text="Play", width=20, state=tk.DISABLED)
        play_button.pack(pady=10)
        return play_button

    @staticmethod
    def create_pause_button(root):
        pause_button = tk.Button(
            root, text="Pause", width=20, state=tk.DISABLED)
        pause_button.pack(pady=10)
        return pause_button

    @staticmethod
    def create_stop_button(root):
        stop_button = tk.Button(root, text="Stop", width=20, state=tk.DISABLED)
        stop_button.pack(pady=10)
        return stop_button

    def __init__(self, root=None, timestamp_label=None, signal_canvas=None, load_audio_button=None,
                 play_button=None, pause_button=None, stop_button=None):
        self.magnification = 1.0
        self.cursor_line = None

        self.root = root or AudioPlayerUi.create_root()
        self.timestamp_label = timestamp_label or AudioPlayerUi.create_timestamp_label(
            self.root)
        self.load_audio_button = load_audio_button or AudioPlayerUi.create_load_audio_button(
            self.root)
        self.play_button = play_button or AudioPlayerUi.create_play_button(
            self.root)
        self.pause_button = pause_button or AudioPlayerUi.create_pause_button(
            self.root)
        self.stop_button = stop_button or AudioPlayerUi.create_stop_button(
            self.root)
        self.signal_canvas = signal_canvas or AudioPlayerUi.create_signal_canvas(
            self.root, self.update_magnification)

    def set_load_button_callback(self, callback):
        self.load_audio_button.configure(command=callback)

    def set_play_button_callback(self, callback):
        self.play_button.configure(command=callback)

    def set_pause_button_callback(self, callback):
        self.pause_button.configure(command=callback)

    def set_stop_button_callback(self, callback):
        self.stop_button.configure(command=callback)

    def mainloop(self):
        self.root.mainloop()

    def get_file_path(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav")])
        if not file_path:
            raise FileNotFoundError()

        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        return file_path

    def play(self):
        self.play_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

    def pause(self):
        self.play_button.config(state=tk.NORMAL)

    def stop(self):
        self.play_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.timestamp_label.config(text=self.TIMESTAMP_START_TEXT)
        self.signal_canvas.delete(self.cursor_line)
        self.cursor_line = None

    def set_audio_signal(self, audio_signal=None):
        if not audio_signal:
            audio_signal = self.audio_signal
        if not audio_signal:
            raise TypeError("Null audio signal")

        self.audio_signal = audio_signal
        self.total_time_label = time.strftime(
            "%M:%S", time.gmtime(self.audio_signal.duration))

    def plot_audio_signal(self):
        if not self.audio_signal:
            raise TypeError("Null audio signal")

        half_height = self.SIGNAL_WINDOW_HEIGHT // 2
        y_values = self.audio_signal.signal * half_height + half_height
        x_values = np.arange(0, self.audio_signal.n_frames)
        magnified_duration = int(
            self.audio_signal.n_frames // self.magnification)
        step_size = max(1, self.audio_signal.n_frames //
                        self.MAX_SIGNAL_SAMPLES)

        # TODO: this needs to be properly updated upon play + pause + play
        start_index = 0
        end_index = min(start_index + magnified_duration,
                        self.audio_signal.n_frames)

        figure, axes = plt.subplots(figsize=(
            self.SIGNAL_WIDTH_INCHES, self.SIGNAL_HEIGHT_INCHES),
            dpi=self.SIGNAL_PLOT_DPI, layout="constrained")
        axes.plot(x_values[start_index:end_index:step_size],
                  y_values[start_index:end_index:step_size])
        axes.set_xlim(start_index, end_index)
        axes.set_ylim(0, self.SIGNAL_WINDOW_HEIGHT)
        axes.axis("off")

        image_buffer = BytesIO()
        figure.savefig(image_buffer, dpi=self.SIGNAL_PLOT_DPI,
                       format="png", pad_inches=0)
        self.signal_image = ImageTk.PhotoImage(Image.open(image_buffer))
        self.signal_canvas.create_image(
            0, 0, image=self.signal_image, anchor="nw")
        self.signal_canvas_width = self.signal_canvas.winfo_width()
        plt.close(figure)

    def set_time_elapsed(self, time_elapsed):
        # TODO: need to set time elapsed via mouse click on signal canvas
        if not self.total_time_label:
            raise TypeError("Null total time label")
        if not self.audio_signal:
            raise TypeError("Null audio signal")
        if not self.signal_canvas_width:
            raise TypeError("Null signal canvas width")

        current_time = time.strftime("%M:%S", time.gmtime(time_elapsed))
        self.timestamp_label.config(
            text=f"Timestamp: {current_time} / {self.total_time_label}")
        # TODO: this needs to be properly updated upon magnification
        cursor_line_x = int((time_elapsed / self.audio_signal.duration)
                            * (self.signal_canvas_width))
        if self.cursor_line:
            self.signal_canvas.delete(self.cursor_line)
        self.cursor_line = self.signal_canvas.create_line(
            cursor_line_x, 0, cursor_line_x, self.SIGNAL_WINDOW_HEIGHT, fill="red", width=2)

    def update_magnification(self, event):
        if not self.audio_signal:
            return

        if event.delta > 0 and self.magnification < 10.0:
            self.magnification *= 1.1
        elif event.delta < 0 and self.magnification > 1.0:
            self.magnification /= 1.1
        self.plot_audio_signal()
