from audio_player_mixer import AudioPlayerMixer
from audio_player_ui import AudioPlayerUi


class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.audio_player_ui = AudioPlayerUi()
        self.audio_player_mixer = AudioPlayerMixer()
        self.audio_player_ui.load_audio_button.configure(command=self.load)
        self.audio_player_ui.play_button.configure(command=self.play)
        self.audio_player_ui.pause_button.configure(command=self.pause)
        self.audio_player_ui.stop_button.configure(command=self.stop)
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
