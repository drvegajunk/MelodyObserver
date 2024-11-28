import pygame


class AudioPlayerMixer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
    
    def load(self, file_path):
        pygame.mixer.music.load(file_path)
    
    def play(self):
        pygame.mixer.music.play()
    
    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()
 