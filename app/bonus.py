import pygame
import time

class Bonus:
    def __init__(self, pos, type_, width, height, duration=5):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_HEIGHT = height
        SCREEN_WIDTH = width
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)
        self.type_ = type_
        self.duration = duration
        self.spawn_time = time.time()
        self.active = True

    def update(self):
        current_time = time.time()
        if current_time - self.spawn_time > self.duration:
            self.active = False

    def draw(self, screen):
        color = (0, 255, 0) if self.type_ == 'life' else (0, 0, 255)
        pygame.draw.rect(screen, color, self.rect)