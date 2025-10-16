import random
import pygame


class Enemy:
    def __init__(self, pos, width, height, size=(32, 32)):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_HEIGHT = height
        SCREEN_WIDTH = width
        self.rect = pygame.Rect(pos[0], pos[1], *size)
        self.speed = random.uniform(1, 3)  # Скорость перемещения каждого врага
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]  # Случайное направление движения

    def move(self):
        # Ограничиваем перемещение врагов пределами экрана
        self.rect.move_ip(self.speed * self.direction[0], self.speed * self.direction[1])

        # Отражаем назад, если достигли края экрана
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction[0] *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.direction[1] *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)