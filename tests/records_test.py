import unittest
import os
import tempfile
from app.records import Records

class TestRecords(unittest.TestCase):
    def setUp(self):
        # Создаем временный файл для тестов
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.filename = self.temp_file.name
        self.temp_file.close()
        self.records = Records(filename=self.filename)

    def tearDown(self):
        # Удаляем временный файл после теста
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_record_positive(self):
        # Тест №1.1: успешное сохранение записи
        data = {'name': 'Player1', 'duration': 12.34, 'difficulty': 'Средний'}
        self.records.save_record(data)
        with open(self.filename, 'r') as f:
            content = f.read()
        self.assertIn('Player1', content)
        self.assertIn('12.34', content)
        self.assertIn('Средний', content)

    def test_load_records_single(self):
        # Тест №2.1: загрузка одного рекорда
        with open(self.filename, 'w') as f:
            f.write('Player2, 15.50, Легкий\n')
        loaded = self.records.load_records()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]['name'], 'Player2')
        self.assertEqual(loaded[0]['duration'], 15.50)
        self.assertEqual(loaded[0]['difficulty'], 'Легкий')

    def test_load_records_empty(self):
        # Тест №2.2: пустой файл
        open(self.filename, 'w').close()
        loaded = self.records.load_records()
        self.assertEqual(loaded, [])

    def test_load_records_no_file(self):
        # Тест №2.3: файл не существует
        # Удаляем файл
        os.remove(self.filename)
        # Создаем экземпляр с несуществующим файлом
        rec = Records(filename=self.filename)
        loaded = rec.load_records()
        self.assertEqual(loaded, [])