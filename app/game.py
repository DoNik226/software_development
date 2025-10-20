import random
import pygame
import time

from app.bonus import Bonus
from app.enemy import Enemy
from app.inputBox import InputBox


class Game:
    def __init__(self, screen, difficulty):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
        self.screen = screen
        self.difficulty = difficulty
        if difficulty == 'Легкий':
            self.spawn_interval = 2000
            self.lives = 3
        elif difficulty == 'Средний':
            self.spawn_interval = 1500
            self.lives = 2
        else:
            self.spawn_interval = 1000
            self.lives = 1
        self.clock = pygame.time.Clock()
        self.player_name = ''
        self.enemies = []
        self.bonuses = []
        self.start_time = None
        self.last_spawn_time = None
        self.elapsed_seconds = None
        self.game_over = False
        self.shield_active = False
        self.shield_start_time = None
        self.last_bonus_time = 0

    def spawn_enemy(self, player_position):
        safe_radius = 3 * 64

        while True:
            new_pos = (
                random.randint(safe_radius, SCREEN_WIDTH - safe_radius - 32),
                random.randint(safe_radius, SCREEN_HEIGHT - safe_radius - 32)
            )
            # Вычисляем расстояние между новой позицией и игроком
            distance_to_player = ((new_pos[0] - player_position[0]) ** 2 +
                                  (new_pos[1] - player_position[1]) ** 2) ** 0.5
            if distance_to_player > safe_radius:
                break

        enemy = Enemy(new_pos, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.enemies.append(enemy)

    def check_collision(self, player_rect):
        collision_occurred = False
        enemies_to_remove = []
        for i, enemy in enumerate(self.enemies):
            if player_rect.colliderect(enemy.rect):
                collision_occurred = True
                enemies_to_remove.append(i)

        for index in reversed(enemies_to_remove):
            del self.enemies[index]

        if collision_occurred and not self.shield_active:
            self.lives -= 1
            if self.lives <= 0:
                print("Игра закончена!")
                return True
        return False

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def game_logic(self, current_time, player_position, player_speed):
        # Перемещение игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_position[1] -= player_speed
        if keys[pygame.K_a]: player_position[0] -= player_speed
        if keys[pygame.K_s]: player_position[1] += player_speed
        if keys[pygame.K_d]: player_position[0] += player_speed

        # Ограничиваем передвижение игрока пределами экрана
        player_position[0] = max(player_position[0], 0)
        player_position[0] = min(player_position[0], SCREEN_WIDTH - self.ship_image.get_width())
        player_position[1] = max(player_position[1], 0)
        player_position[1] = min(player_position[1], SCREEN_HEIGHT - self.ship_image.get_height())

        # Спавн врагов
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_enemy(player_position)
            self.last_spawn_time = current_time

        # Обновляем положение и активность бонусов
        for bonus in self.bonuses[:]:
            bonus.update()
            if not bonus.active:
                self.bonuses.remove(bonus)

        # Проверка столкновений с врагами
        player_rect = pygame.Rect(*player_position, self.ship_image.get_width(), self.ship_image.get_height())
        if self.check_collision(player_rect):
            return False

        # Появление новых бонусов каждые 7 секунд
        if current_time - self.last_bonus_time > 7000:
            bonus_type = random.choice(['shield', 'life'])
            bonus_pos = [
                random.randint(32, SCREEN_WIDTH - 64),
                random.randint(32, SCREEN_HEIGHT - 64)
            ]
            bonus = Bonus(bonus_pos, bonus_type, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.bonuses.append(bonus)
            self.last_bonus_time = current_time

        # Проверка столкновений с бонусами
        for bonus in self.bonuses[:]:
            if player_rect.colliderect(bonus.rect):
                if bonus.type_ == 'shield':
                    self.shield_active = True
                    self.shield_start_time = time.time()
                elif bonus.type_ == 'life':
                    self.lives += 1
                self.bonuses.remove(bonus)

        # Время действия щита истекло?
        if self.shield_active and time.time() - self.shield_start_time > 5:
            self.shield_active = False

        return True

    def render_game(self, player_position, formatted_time):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.ship_image, tuple(player_position))

        # Рендер таймера
        font = pygame.font.SysFont(None, 32)
        timer_text = font.render(f"Время: {formatted_time}", True, (255, 255, 255))
        lives_text = font.render(f'Жизни: {self.lives}', True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        # Рендер щитов
        if self.shield_active:
            remaining_shield_time = max(0, 5 - (time.time() - self.shield_start_time))
            shield_timer_text = font.render(f'Щит: {remaining_shield_time:.1f} сек.', True, (255, 255, 255))
            self.screen.blit(shield_timer_text, (10, 80))

        #Рисуем врагов
        for enemy in self.enemies:
            enemy.move()
            enemy.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)

        pygame.display.flip()

    def collect_results(self):
        input_box = InputBox(self.screen)
        done = False
        while not done:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.player_name = input_box.text.rstrip('\n')
                    done = True
                else:
                    input_box.update([event])
            input_box.draw(self.screen)
            pygame.display.flip()
        return {
            'name': self.player_name,
            'duration': self.elapsed_seconds,
            'difficulty': self.difficulty
        }

    def run_game(self):
        player_position = [400, 300]
        player_speed = 5
        original_ship_image = pygame.image.load('../assets/ship1.gif')
        ship_size = (64, 64)
        self.ship_image = pygame.transform.scale(original_ship_image, ship_size)

        running = True
        self.last_spawn_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks() / 1000
        while running:
            current_time = pygame.time.get_ticks()
            self.elapsed_seconds = (current_time - self.start_time * 1000) / 1000
            formatted_time = self.format_time(self.elapsed_seconds)

            if not self.process_events():
                break

            running = self.game_logic(current_time, player_position, player_speed)

            self.render_game(player_position, formatted_time)

            self.clock.tick(60)

        results = self.collect_results()
        return results