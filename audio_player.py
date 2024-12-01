from audio_player_mixer import AudioPlayerMixer
from audio_player_ui import AudioPlayerUi
from audio_signal import AudioSignal
import threading
import time


class AudioPlayer:
    UPDATE_TIMESTAMP_INTERVAL = 0.10

    def __init__(self, audio_player_ui=AudioPlayerUi(), audio_player_mixer=AudioPlayerMixer()):
        self.is_playing = False
        self.audio_player_ui = audio_player_ui
        self.audio_player_mixer = audio_player_mixer

        self.audio_player_ui.set_load_button_callback(self.load)
        self.audio_player_ui.set_play_button_callback(self.play)
        self.audio_player_ui.set_pause_button_callback(self.pause)
        self.audio_player_ui.set_stop_button_callback(self.stop)
        self.audio_player_ui.mainloop()

    def load(self):
        file_path = self.audio_player_ui.get_file_path()
        self.audio_player_mixer.load(file_path)
        self.audio_signal = AudioSignal(file_path)
        self.audio_player_ui.set_audio_signal(self.audio_signal)
        self.audio_player_ui.plot_audio_signal()

    def play(self):
        if self.is_playing:
            return

        self.is_playing = True
        self.audio_player_mixer.play()
        self.audio_player_ui.play()
        threading.Thread(target=self.send_play_timestamp).start()

    def pause(self):
        if not self.is_playing:
            return

        self.is_playing = False
        self.audio_player_mixer.pause()
        self.audio_player_ui.pause()

    def stop(self):
        self.is_playing = False
        self.audio_player_mixer.stop()
        self.audio_player_ui.stop()

    def send_play_timestamp(self):
        while self.is_playing:
            audio_time_elapsed = self.audio_player_mixer.get_time_elapsed()
            self.audio_player_ui.set_time_elapsed(audio_time_elapsed)
            time.sleep(self.UPDATE_TIMESTAMP_INTERVAL)


if __name__ == "__main__":
    AudioPlayer()
