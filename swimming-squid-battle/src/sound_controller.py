import traceback

import pygame

from .env import *


def sound_enabled(func):
    def wrapper(self, *args, **kwargs):
        if self._is_sound_on:
            return func(self, *args, **kwargs)

    return wrapper


class SoundController():
    def __init__(self, is_sound_on):
        self._is_sound_on = bool(is_sound_on == "on")
        if self._is_sound_on:
            self.load_sounds()

    def load_sounds(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path.join(MUSIC_PATH, "bgm.mp3"))
            pygame.mixer.music.set_volume(0.6)
            self._eating_good = pygame.mixer.Sound(path.join(SOUND_PATH, "eat_good_food.mp3"))
            self._eating_bad = pygame.mixer.Sound(path.join(SOUND_PATH, "eat_bad_food.mp3"))
            self._pass = pygame.mixer.Sound(path.join(SOUND_PATH, "pass.mp3"))
            self._fail = pygame.mixer.Sound(path.join(SOUND_PATH, "fail.mp3"))
            self._lv_up = pygame.mixer.Sound(path.join(SOUND_PATH, "lv_up.mp3"))
            self._lv_down = pygame.mixer.Sound(path.join(SOUND_PATH, "lv_down.mp3"))
            self._collision = pygame.mixer.Sound(path.join(SOUND_PATH, "collision.mp3"))
        except Exception as e :
            self._is_sound_on = False
            traceback.print_exc()

    @sound_enabled
    def play_music(self):
        pygame.mixer.music.play(-1)

    @sound_enabled
    def play_eating_good(self):
        self._eating_good.play()

    @sound_enabled
    def play_eating_bad(self):
        self._eating_bad.play()
    @sound_enabled
    def play_cheer(self):
        self._pass.play()

    @sound_enabled
    def play_fail(self):
        self._fail.play()
    @sound_enabled
    def play_lv_up(self):
        self._lv_up.play()

    @sound_enabled
    def play_lv_down(self):
        self._lv_down.play()

    @sound_enabled
    def play_collision(self):
        self._collision.play()
