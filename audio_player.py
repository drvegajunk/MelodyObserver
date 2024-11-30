from audio_player_mixer import AudioPlayerMixer
from audio_player_ui import AudioPlayerUi


class AudioPlayer:
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
        file_path = self.audio_player_ui.load()
        self.audio_player_mixer.load(file_path)

    def play(self):
        if self.is_playing:
            return
        self.audio_player_mixer.play()
        self.audio_player_ui.play()
        self.is_playing = True

    def pause(self):
        if not self.is_playing:
            return
        self.audio_player_mixer.pause()
        self.audio_player_ui.pause()
        self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.audio_player_mixer.stop()
        self.audio_player_ui.stop()


if __name__ == "__main__":
    AudioPlayer()
