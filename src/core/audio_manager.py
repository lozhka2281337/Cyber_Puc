import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        
    def play_bgm(self, file_path, loops=-1, volume=1):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    def queue_bgm(self, file_path):
        pygame.mixer.music.queue(file_path)

    def set_bgm_volume(self, volume):
        volume = max(0.0, min(1.0, volume)) 
        pygame.mixer.music.set_volume(volume)

    def get_bgm_volume(self):
        return pygame.mixer.music.get_volume()

    def stop_bgm(self):
        pygame.mixer.music.stop()

    def bgm_is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()