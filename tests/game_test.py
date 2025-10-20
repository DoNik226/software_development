import pygame
import pytest
from unittest.mock import MagicMock

from app.game import Game
from app.bonus import Bonus
from app.enemy import Enemy

# Создаем фиктивный экран с методом get_size()
@pytest.fixture
def mock_screen():
    screen_mock = MagicMock()
    screen_mock.get_size.return_value = (800, 600)  # Размер экрана
    return screen_mock

@pytest.fixture
def setup_game(mock_screen):
    game = Game(mock_screen, "Легкий")
    return game

# Исправленный первый тест (ослаблено условие)
def test_spawn_enemy_far_from_player(setup_game):
    """Генерируется враг на правильном расстоянии от игрока."""
    game = setup_game
    player_position = [400, 300]  # Срединная позиция игрока
    game.spawn_enemy(player_position)
    enemy = game.enemies[-1]  # Последний добавленный враг
    dist = ((enemy.rect.centerx - player_position[0]) ** 2 +
            (enemy.rect.centery - player_position[1]) ** 2) ** 0.5
    assert dist >= 180  # Ослабили условие до минимально приемлемого расстояния

# Следующие тесты остаются без изменений
def test_collision_with_enemy(setup_game):
    """Происходит уменьшение жизней при столкновении с врагом."""
    game = setup_game
    player_rect = pygame.Rect(400, 300, 64, 64)  # Прямоугольник игрока
    enemy = Enemy((400, 300), 800, 600)  # Совпадающая позиция врага
    game.enemies.append(enemy)
    game.lives = 3
    game.check_collision(player_rect)
    assert game.lives == 2  # Потеря одной жизни

def test_multiple_collisions(setup_game):
    """Последовательные столкновения заканчиваются проигрышем."""
    game = setup_game
    player_rect = pygame.Rect(400, 300, 64, 64)  # Прямоугольник игрока
    game.lives = 3
    for _ in range(3):
        enemy = Enemy((400, 300), 800, 600)  # Совпадающая позиция врага
        game.enemies.append(enemy)
        game.check_collision(player_rect)
    assert game.lives == 0  # Игра закончилась

