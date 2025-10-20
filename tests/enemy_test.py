import pytest
import pygame

from enemy import Enemy

global SCREEN_WIDTH, SCREEN_HEIGHT
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

# Тест №1.1 (позитивный)
def test_normal_movement():
    """Нормальное перемещение объекта внутри экрана."""
    enemy = Enemy((100, 100), SCREEN_WIDTH, SCREEN_HEIGHT)
    enemy.speed = 1  # установим фиксированную скорость для точности
    enemy.direction = [1, 1]  # направим вправо-вниз

    # Несколько итераций шага
    for _ in range(10):
        enemy.move()

    # Проверка результата
    assert enemy.rect.x > 100  # Должен сместиться вправо
    assert enemy.rect.y > 100  # Должен сместиться вниз
    assert enemy.rect.x < SCREEN_WIDTH  # Не вышел за правую границу
    assert enemy.rect.y < SCREEN_HEIGHT  # Не вышел за нижнюю границу


# Тест №1.2 (негативный)
def test_edge_reflection():
    """Перемещение около края экрана и отражение."""
    enemy = Enemy((1595, 100), SCREEN_WIDTH, SCREEN_HEIGHT)
    enemy.speed = 1  # увеличим скорость для быстрого достижения края
    enemy.direction = [1, 1]  # направим опять вправо-вниз

    # Сделаем несколько шагов
    for _ in range(9):
        enemy.move()

    # Должен достигнуть правого края и развернуться
    assert enemy.rect.x < SCREEN_WIDTH  # Проверим, что не вышел за границу
    assert enemy.direction[0] == -1  # Изменилось направление по X


# Тест №1.3 (негативный)
def test_low_speed():
    """Объект почти не двигается при низкой скорости."""
    enemy = Enemy((100, 100), SCREEN_WIDTH, SCREEN_HEIGHT)
    enemy.speed = 0.001  # Минимально возможная скорость
    enemy.direction = [1, 1]

    # Даже большое количество шагов почти не сдвинет объект
    for _ in range(1000):
        enemy.move()

    # Практически никакого заметного движения
    assert abs(enemy.rect.x - 100) < 1  # едва заметно смещается

    assert abs(enemy.rect.y - 100) < 1  # минимальное отклонение
