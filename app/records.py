import sqlite3


class Records:
    def __init__(self, filename="../data/records.txt"):
        self.filename = filename

    def save_record(self, data):
        with open(self.filename, "a") as file:
            file.write(f"{data['name']}, {data['duration']:.2f}, {data['difficulty']}\n")

    def load_records(self):
        try:
            with open(self.filename, "r") as file:
                lines = file.readlines()
                records = []
                for line in lines:
                    parts = line.strip().split(',')
                    records.append({
                        'name': parts[0].strip(),
                        'duration': float(parts[1]),
                        'difficulty': parts[2].strip()
                    })

                # Сортируем по сложности (первичный критерий) и длительности (вторичный критерий)
                # ЧЕМ НИЗЖЕ сложность (т.е., ближе к 1), ТЕМ ВЫШЕ РЕЙТИНГ
                # Внутри сложности — сортируем ПО УБАВЛЕНИЮ времени
                sorted_records = sorted(records,
                                        key=lambda r: ({"Сложный": 1, "Средний": 2, "Легкий": 3}[r['difficulty']],
                                                       -r['duration']))  # Меняем знак, чтобы было по убыванию
                return sorted_records
        except FileNotFoundError:
            return []