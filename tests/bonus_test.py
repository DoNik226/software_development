import unittest
import time

from app.bonus import Bonus


class TestBonus(unittest.TestCase):
    def setUp(self):
        # Создаем бонус с продолжительностью 5 секунд
        self.bonus = Bonus(pos=(0,0), type_='life', width=100, height=100, duration=5)

    def test_update_positive(self):
        # Тест №1.1: активность должна стать False после истечения времени
        self.bonus.spawn_time = time.time() - 6  # время появления более 6 секунд назад
        self.bonus.update()
        self.assertFalse(self.bonus.active)

    def test_update_negative(self):
        # Тест №1.2: активность должна остаться True, если время не истекло
        self.bonus.spawn_time = time.time() - 2  # время появления 2 секунды назад
        self.bonus.update()
        self.assertTrue(self.bonus.active)

