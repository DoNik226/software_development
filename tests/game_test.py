import time
import unittest
from unittest import mock

import pygame
import pytest
from unittest.mock import MagicMock, patch, Mock

from app.game import Game
from app.bonus import Bonus
from app.enemy import Enemy
from app.inputBox import InputBox


@pytest.fixture
def mock_screen():
    screen_mock = MagicMock()
    screen_mock.get_size.return_value = (800, 600)
    return screen_mock

@pytest.fixture
def setup_game(mock_screen):
    game = Game(mock_screen, "Легкий")
    game.elapsed_seconds = 123
    return game

@pytest.fixture
def setup_input_box(mock_screen):
    inputBox = InputBox(mock_screen)
    return inputBox

def create_keydown_event(key, unicode_char=''):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "unicode": unicode_char})

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()

def test_difficulty_easy(mock_screen):
    game = Game(mock_screen, 'Легкий')
    assert game.spawn_interval == 2000 and game.lives == 3

def test_difficulty_medium(mock_screen):
    game = Game(mock_screen, 'Средний')
    assert game.spawn_interval == 1500 and game.lives == 2

def test_difficulty_hard(mock_screen):
    game = Game(mock_screen, 'Сложный')
    assert game.spawn_interval == 1000 and game.lives == 1

def test_spawn_enemy_far_from_player(setup_game):
    game = setup_game
    player_position = [400, 300]
    game.spawn_enemy(player_position)
    enemy = game.enemies[-1]
    dist = ((enemy.rect.centerx - player_position[0]) ** 2 +
            (enemy.rect.centery - player_position[1]) ** 2) ** 0.5
    assert dist >= 170

def test_collision_with_enemy(setup_game):
    game = setup_game
    player_rect = pygame.Rect(400, 300, 64, 64)
    enemy = Enemy((400, 300), 800, 600)
    game.enemies.append(enemy)
    game.lives = 3
    game.check_collision(player_rect)
    assert game.lives == 2

def test_multiple_collisions(setup_game):
    game = setup_game
    player_rect = pygame.Rect(400, 300, 64, 64)
    game.lives = 3
    for _ in range(3):
        enemy = Enemy((400, 300), 800, 600)
        game.enemies.append(enemy)
        game.check_collision(player_rect)
    assert game.lives == 0

def test_format_time_multiple_minutes_and_seconds(setup_game):
    game = setup_game
    result = game.format_time(123)
    expected_result = "2:03"
    assert result == expected_result

def test_format_time_large_number_of_seconds(setup_game):
    game = setup_game
    result = game.format_time(3661)
    expected_result = "61:01"
    assert result == expected_result

def test_escape_pressed(setup_game):
    escape_event = create_keydown_event(pygame.K_ESCAPE)
    with unittest.mock.patch('pygame.event.get', return_value=[escape_event]):
        result = setup_game.process_events()
        assert result == False

def test_other_keys_pressed(setup_game):
    other_key_event = create_keydown_event(pygame.K_SPACE)
    with unittest.mock.patch('pygame.event.get', return_value=[other_key_event]):
        result = setup_game.process_events()
        assert result == True

@pytest.fixture
def game():
    mock_screen = Mock()
    mock_screen.get_size.return_value = (800, 600)
    game = Game(mock_screen, 'Легкий')
    game.ship_image = Mock()
    game.ship_image.get_width.return_value = 64
    game.ship_image.get_height.return_value = 64
    game.last_spawn_time = 0
    game.last_bonus_time = 0
    game.enemies = []
    game.bonuses = []
    game.lives = 3
    game.shield_active = False
    game.shield_start_time = None
    game.spawn_interval = 2000
    return game

def test_player_movement(game):
    player_position = [400, 300]
    player_speed = 5

    with patch('pygame.key.get_pressed') as mock_keys:
        mock_keys.return_value = {
            pygame.K_w: True,
            pygame.K_a: False,
            pygame.K_s: False,
            pygame.K_d: False
        }

        result = game.game_logic(1000, player_position, player_speed)

        assert player_position == [400, 295]
        assert result is True

def test_enemy_spawn(game):
    player_position = [400, 300]
    game.last_spawn_time = 0
    game.spawn_interval = 1000

    result = game.game_logic(2000, player_position, 5)

    assert len(game.enemies) == 1
    assert result is True

def test_collision_with_enemy(game):
    player_position = [400, 300]

    enemy = Mock()
    enemy.rect = pygame.Rect(400, 300, 32, 32)
    game.enemies = [enemy]
    game.lives = 3

    result = game.game_logic(1000, player_position, 5)

    assert game.lives == 2
    assert len(game.enemies) == 0
    assert result is True

def test_game_over(game):
    player_position = [400, 300]

    enemy = Mock()
    enemy.rect = pygame.Rect(400, 300, 32, 32)
    game.enemies = [enemy]
    game.lives = 1

    result = game.game_logic(1000, player_position, 5)

    assert result is False

def test_shield_protection(game):
    player_position = [400, 300]

    enemy = Mock()
    enemy.rect = pygame.Rect(400, 300, 32, 32)
    game.enemies = [enemy]
    game.lives = 3
    game.shield_active = True
    game.shield_start_time = time.time()

    with patch('pygame.key.get_pressed') as mock_keys, \
            patch('pygame.Rect') as mock_rect, \
            patch('time.time') as mock_time:
        mock_keys.return_value = {pygame.K_w: False, pygame.K_a: False,
                                  pygame.K_s: False, pygame.K_d: False}

        mock_rect_instance = Mock()
        mock_rect.return_value = mock_rect_instance

        mock_time.return_value = game.shield_start_time + 2

        result = game.game_logic(1000, player_position, 5)

    assert game.lives == 3
    assert len(game.enemies) == 0
    assert result is True

def test_bonus_spawn(game):
    player_position = [400, 300]
    game.last_bonus_time = 0

    result = game.game_logic(8000, player_position, 5)

    assert len(game.bonuses) == 1
    assert result is True

def test_life_bonus_collection(game):
    player_position = [400, 300]
    game.lives = 3

    bonus = Mock()
    bonus.rect = pygame.Rect(400, 300, 32, 32)
    bonus.type_ = 'life'
    bonus.active = True
    game.bonuses = [bonus]

    result = game.game_logic(1000, player_position, 5)

    assert game.lives == 4
    assert len(game.bonuses) == 0
    assert result is True

def test_shield_bonus_collection(game):
    player_position = [400, 300]
    game.shield_active = False

    bonus = Mock()
    bonus.rect = pygame.Rect(400, 300, 32, 32)
    bonus.type_ = 'shield'
    bonus.active = True
    game.bonuses = [bonus]

    with patch('time.time') as mock_time:
        mock_time.return_value = 1000
        result = game.game_logic(1000, player_position, 5)

    assert game.shield_active is True
    assert game.shield_start_time == 1000
    assert len(game.bonuses) == 0
    assert result is True

def test_shield_expiration(game):
    player_position = [400, 300]
    game.shield_active = True
    game.shield_start_time = time.time() - 6

    result = game.game_logic(1000, player_position, 5)

    assert game.shield_active is False
    assert result is True

def test_screen_boundaries(game):
    player_position = [0, 0]
    player_speed = 10

    with patch('pygame.key.get_pressed') as mock_keys:
        mock_keys.return_value = {
            pygame.K_w: True,
            pygame.K_a: True,
            pygame.K_s: False,
            pygame.K_d: False
        }

        result = game.game_logic(1000, player_position, player_speed)

        assert player_position == [0, 0]
        assert result is True


class TestRunGame:
    @pytest.fixture
    def game(self):
        mock_screen = Mock()
        mock_screen.get_size.return_value = (800, 600)
        game = Game(mock_screen, 'Легкий')

        game.clock = Mock()
        game.clock.tick.return_value = None

        return game

    def test_run_game_initialization(self, game):
        with patch('pygame.image.load') as mock_load, \
                patch('pygame.transform.scale') as mock_scale, \
                patch('pygame.time.get_ticks') as mock_ticks, \
                patch.object(game, 'process_events') as mock_events, \
                patch.object(game, 'game_logic') as mock_logic, \
                patch.object(game, 'render_game') as mock_render, \
                patch.object(game, 'collect_results') as mock_collect:

            mock_ship_image = Mock()
            mock_load.return_value = mock_ship_image
            mock_scale.return_value = mock_ship_image
            mock_ticks.return_value = 1000
            mock_events.return_value = False
            mock_collect.return_value = {'name': 'Test', 'duration': 0, 'difficulty': 'Легкий'}

            results = game.run_game()

            mock_load.assert_called_once_with('../assets/ship1.gif')
            mock_scale.assert_called_once_with(mock_ship_image, (64, 64))
            assert game.ship_image == mock_ship_image
            assert game.last_spawn_time == 1000
            assert game.start_time == 1

            mock_collect.assert_called_once()
            assert results['name'] == 'Test'

    def test_run_game_game_over(self, game):
        with patch('pygame.image.load') as mock_load, \
                patch('pygame.transform.scale') as mock_scale, \
                patch('pygame.time.get_ticks') as mock_ticks, \
                patch.object(game, 'process_events') as mock_events, \
                patch.object(game, 'game_logic') as mock_logic, \
                patch.object(game, 'render_game') as mock_render, \
                patch.object(game, 'collect_results') as mock_collect:
            mock_ship_image = Mock()
            mock_load.return_value = mock_ship_image
            mock_scale.return_value = mock_ship_image

            call_count = 0

            def get_ticks_side_effect():
                nonlocal call_count
                result = call_count * 100
                call_count += 1
                return result

            mock_ticks.side_effect = get_ticks_side_effect

            mock_events.return_value = True
            mock_logic.return_value = False

            mock_collect.return_value = {
                'name': 'Player2',
                'duration': 0.1,
                'difficulty': 'Легкий'
            }

            results = game.run_game()

            mock_events.assert_called_once()
            mock_logic.assert_called_once()
            mock_render.assert_called_once()

            mock_collect.assert_called_once()
            assert abs(results['duration'] - 0.1) < 1e-9

    def test_run_game_time_calculation(self, game):
        with patch('pygame.image.load') as mock_load, \
                patch('pygame.transform.scale') as mock_scale, \
                patch('pygame.time.get_ticks') as mock_ticks, \
                patch.object(game, 'process_events') as mock_events, \
                patch.object(game, 'game_logic') as mock_logic, \
                patch.object(game, 'render_game') as mock_render, \
                patch.object(game, 'collect_results') as mock_collect:
            mock_ship_image = Mock()
            mock_load.return_value = mock_ship_image
            mock_scale.return_value = mock_ship_image

            call_count = 0

            def get_ticks_side_effect():
                nonlocal call_count
                result = call_count * 1000
                call_count += 1
                return result

            mock_ticks.side_effect = get_ticks_side_effect

            mock_events.side_effect = [True, True, True, True, False]
            mock_logic.return_value = True

            mock_collect.return_value = {
                'name': 'Player3',
                'duration': 4.0,
                'difficulty': 'Легкий'
            }

            results = game.run_game()
            assert results['duration'] == 4

    def test_run_game_different_difficulties(self):
        difficulties = ['Легкий', 'Средний', 'Сложный']
        expected_lives = [3, 2, 1]
        expected_intervals = [2000, 1500, 1000]

        for i, difficulty in enumerate(difficulties):
            mock_screen = Mock()
            mock_screen.get_size.return_value = (800, 600)
            game = Game(mock_screen, difficulty)

            assert game.difficulty == difficulty
            assert game.lives == expected_lives[i]
            assert game.spawn_interval == expected_intervals[i]

    def test_run_game_exception_handling(self, game):
        with patch('pygame.image.load') as mock_load, \
                patch('pygame.transform.scale') as mock_scale, \
                patch('pygame.time.get_ticks') as mock_ticks, \
                patch.object(game, 'process_events') as mock_events, \
                patch.object(game, 'game_logic') as mock_logic, \
                patch.object(game, 'render_game') as mock_render, \
                patch.object(game, 'collect_results') as mock_collect:
            mock_ship_image = Mock()
            mock_load.return_value = mock_ship_image
            mock_scale.return_value = mock_ship_image

            call_count = 0

            def get_ticks_side_effect():
                nonlocal call_count
                result = call_count * 100
                call_count += 1
                return result

            mock_ticks.side_effect = get_ticks_side_effect

            mock_events.side_effect = [
                True,
                Exception("Test exception"),
            ]
            mock_logic.return_value = True

            mock_collect.return_value = {
                'name': 'Player4',
                'duration': 0.1,
                'difficulty': 'Легкий'
            }

            with pytest.raises(Exception, match="Test exception"):
                game.run_game()

    def test_run_game_resource_cleanup(self, game):
        with patch('pygame.image.load') as mock_load, \
                patch('pygame.transform.scale') as mock_scale, \
                patch('pygame.time.get_ticks') as mock_ticks, \
                patch.object(game, 'process_events') as mock_events, \
                patch.object(game, 'game_logic') as mock_logic, \
                patch.object(game, 'render_game') as mock_render, \
                patch.object(game, 'collect_results') as mock_collect:
            mock_ship_image = Mock()
            mock_load.return_value = mock_ship_image
            mock_scale.return_value = mock_ship_image
            mock_ticks.return_value = 1000

            mock_events.return_value = False
            mock_collect.return_value = {'name': 'Test', 'duration': 0, 'difficulty': 'Легкий'}

            results = game.run_game()

            mock_load.assert_called_once()
            mock_scale.assert_called_once()
            mock_events.assert_called_once()
            mock_collect.assert_called_once()


class TestCollectResults:
    @pytest.fixture
    def game(self):
        mock_screen = Mock()
        mock_screen.get_size.return_value = (800, 600)
        game = Game(mock_screen, 'Легкий')
        game.elapsed_seconds = 120.5
        return game

    def test_collect_results_normal_flow(self, game):
        with patch('app.game.InputBox') as mock_input_box_class, \
                patch('pygame.event.get') as mock_events, \
                patch('pygame.display.flip') as mock_flip:
            mock_input_box = Mock()
            mock_input_box.text = "TestPlayer\n"
            mock_input_box_class.return_value = mock_input_box

            mock_events.side_effect = [
                [Mock(type=pygame.KEYDOWN, key=pygame.K_a)],
                [Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN)]
            ]

            results = game.collect_results()

            mock_input_box_class.assert_called_once_with(game.screen)

            assert mock_input_box.update.call_count >= 1
            assert mock_input_box.draw.call_count >= 1

            assert results == {
                'name': 'TestPlayer',
                'duration': 120.5,
                'difficulty': 'Легкий'
            }
            assert game.player_name == 'TestPlayer'

    def test_collect_results_empty_name(self, game):
        with patch('app.game.InputBox') as mock_input_box_class, \
                patch('pygame.event.get') as mock_events, \
                patch('pygame.display.flip') as mock_flip:
            mock_input_box = Mock()
            mock_input_box.text = "\n"
            mock_input_box_class.return_value = mock_input_box

            mock_events.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN)]

            results = game.collect_results()

            assert results['name'] == ''
            assert game.player_name == ''


    def test_collect_results_with_different_difficulties(self):
        difficulties = ['Легкий', 'Средний', 'Сложный']

        for difficulty in difficulties:
            mock_screen = Mock()
            mock_screen.get_size.return_value = (800, 600)
            game = Game(mock_screen, difficulty)
            game.elapsed_seconds = 90.0

            with patch('app.game.InputBox') as mock_input_box_class, \
                    patch('pygame.event.get') as mock_events, \
                    patch('pygame.display.flip') as mock_flip:
                mock_input_box = Mock()
                mock_input_box.text = f"Player_{difficulty}\n"
                mock_input_box_class.return_value = mock_input_box

                mock_events.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN)]

                results = game.collect_results()

                assert results['difficulty'] == difficulty
                assert results['name'] == f"Player_{difficulty}"






