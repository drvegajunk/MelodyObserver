import pygame
import time


class AudioPlayerMixer:
    def __init__(self):
        self.audio_time_elapsed = 0.0
        self.last_play_timestamp = None
        self.paused_then_played = False
        pygame.init()
        pygame.mixer.init()

    def load(self, file_path):
        pygame.mixer.music.unload()
        pygame.mixer.music.load(file_path)

    def play(self):
        if self.audio_time_elapsed:
            self.paused_then_played = True
        self.last_play_timestamp = time.time()
        pygame.mixer.music.play(start=self.audio_time_elapsed)

    def pause(self):
        if not self.last_play_timestamp:
            raise ValueError("Played before pause")

        self.paused_then_played = False
        self.audio_time_elapsed += time.time() - self.last_play_timestamp
        pygame.mixer.music.pause()

    def stop(self):
        self.audio_time_elapsed = 0.0
        self.last_play_timestamp = None
        pygame.mixer.music.stop()

    def get_time_elapsed(self):
        if self.last_play_timestamp and (not self.audio_time_elapsed
                                         or self.paused_then_played):
            return time.time() - self.last_play_timestamp + self.audio_time_elapsed
        return self.audio_time_elapsed
