import pygame
from records import Records


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.records = Records()
        self.width, self.height = screen.get_size()  # Получаем ширину и высоту экрана


    def center_text(self, surface, y_pos):
        """Центрировать текст по горизонтали"""
        rect = surface.get_rect(center=(self.width // 2, y_pos))
        return rect

    def show_menu(self):
        font = pygame.font.Font(None, 36)
        buttons = [
            ('Играть', lambda: 'play'),
            ('Рекорды', lambda: 'records'),
            ('Помощь', lambda: 'help'),
            ('Выход', lambda: 'exit')
        ]

        selected_button = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_button -= 1
                    elif event.key == pygame.K_DOWN:
                        selected_button += 1
                    elif event.key == pygame.K_RETURN:
                        return buttons[selected_button][1]()

                    selected_button %= len(buttons)

            self.screen.fill((0, 0, 0))  # Черный фон

            y_pos = self.height // 2 - len(buttons) * 25  # Центровка кнопок вертикально
            for i, button in enumerate(buttons):
                color = (255, 255, 255) if i != selected_button else (0, 255, 0)
                text_surface = font.render(button[0], True, color)
                rect = self.center_text(text_surface, y_pos)
                self.screen.blit(text_surface, rect)
                y_pos += 50

            pygame.display.flip()

    def select_level(self):
        font = pygame.font.Font(None, 36)
        levels = ['Легкий', 'Средний', 'Сложный']
        selected_level = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected_level -= 1
                    elif event.key == pygame.K_RIGHT:
                        selected_level += 1
                    elif event.key == pygame.K_RETURN:
                        return levels[selected_level]

                    selected_level %= len(levels)

            self.screen.fill((0, 0, 0))

            # Центровка уровней горизонтально
            x_pos = self.width // 2 - len(levels) * 75 // 2  # Средняя точка по оси X минус половина суммарной длины
            y_pos = self.height // 2  # Уровень сложности располагается по центру экрана по вертикали

            for i, level in enumerate(levels):
                color = (255, 255, 255) if i != selected_level else (0, 255, 0)
                text_surface = font.render(level, True, color)
                rect = text_surface.get_rect(
                    center=(x_pos + i * 150, y_pos))  # Централизуем каждую надпись по своей позиции
                self.screen.blit(text_surface, rect)

            pygame.display.flip()

    def show_records(self):
        font = pygame.font.Font(None, 36)  # Единообразный шрифт для заголовков и данных

        records = self.records.load_records()

        scroll_offset = 0  # Смещение для прокрутки
        visible_rows = (self.height - 100) // 40  # Максимальное количество строк, которые видны одновременно
        total_rows = len(records)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        scroll_offset = max(scroll_offset - 1, 0)  # Прокручиваем вверх
                    elif event.key == pygame.K_DOWN and total_rows - visible_rows > 0:
                        scroll_offset = min(scroll_offset + 1, total_rows - visible_rows)  # Прокручиваем вниз

            self.screen.fill((0, 0, 0))  # Чёрный фон

            # Параметры таблицы
            padding = 20  # Общий отступ от краев экрана
            column_width_ratio = [0.1, 0.25, 0.4, 0.25]  # Пропорции ширины столбцов
            column_widths = [w * (self.width - 2 * padding) for w in column_width_ratio]
            table_x = padding
            table_y = padding
            row_height = 40  # Высота одной строки
            header_height = 60  # Высота заголовочной строки

            # Заголовки таблицы
            title_headers = ["Место", "Имя игрока", "Продолжительность (сек)", "Сложность"]

            # Линия сетки таблицы
            # Горизонтальные линии
            pygame.draw.line(self.screen, (255, 255, 255), (table_x, table_y), (table_x + sum(column_widths), table_y),
                             2)
            pygame.draw.line(self.screen, (255, 255, 255), (table_x, table_y + header_height),
                             (table_x + sum(column_widths), table_y + header_height), 2)
            for i in range(visible_rows + 1):
                pygame.draw.line(self.screen, (255, 255, 255), (table_x, table_y + header_height + i * row_height),
                                 (table_x + sum(column_widths), table_y + header_height + i * row_height), 2)

            # Вертикальные линии
            current_x = table_x
            for width in column_widths:
                pygame.draw.line(self.screen, (255, 255, 255), (current_x, table_y),
                                 (current_x, table_y + header_height + visible_rows * row_height), 2)
                current_x += width
            # Крайняя правая линия
            pygame.draw.line(self.screen, (255, 255, 255), (current_x, table_y),
                             (current_x, table_y + header_height + visible_rows * row_height), 2)

            # Наполнение таблицы данными
            # Заголовки
            x_offset = table_x
            for idx, header in enumerate(title_headers):
                text_surface = font.render(header, True, (255, 255, 0))  # Жёлтый цвет заголовков
                text_rect = text_surface.get_rect(midtop=(x_offset + column_widths[idx] / 2, table_y + padding))
                self.screen.blit(text_surface, text_rect)
                x_offset += column_widths[idx]

            # Данные игроков
            y_pos = table_y + header_height
            displayed_records = records[scroll_offset:scroll_offset + visible_rows]
            for idx, record in enumerate(displayed_records):
                # Расчёт истинного индекса (места) основываясь на глобальном индексе записей
                true_row_idx = scroll_offset + idx + 1  # Поскольку нумерация с 1-го места
                columns = [
                    str(true_row_idx),
                    record["name"],
                    "{:.2f}".format(record["duration"]),
                    record["difficulty"].capitalize()
                ]

                x_offset = table_x
                for col_idx, value in enumerate(columns):
                    text_surface = font.render(value, True, (255, 255, 255))  # Белый цвет данных
                    text_rect = text_surface.get_rect(midleft=(x_offset + padding, y_pos + padding))
                    self.screen.blit(text_surface, text_rect)
                    x_offset += column_widths[col_idx]

                y_pos += row_height

            pygame.display.flip()

    def show_help(self):
        title_font = pygame.font.SysFont('arial', 48, bold=True)  # Заголовочный шрифт
        content_font = pygame.font.SysFont('verdana', 24)  # Основной шрифт

        help_title = "Справка по игре Космический боец"
        help_lines = [
            ("Управление:", ["WASD - движение"]),
            ("Выход:", ["ESC - выход из игры"]),
            ("Типы сущностей:", [
                "- Красные: Противники, столкновение отнимает одну жизнь.",
                "- Зелёные: Бонусы, увеличивают количество жизней на 1.",
                "- Синие: Щиты, обеспечивают временную защиту."
            ]),
            ("Режимы сложности:", [
                "- Легкий: Начальные жизни - 3, появление врагов каждые 2 сек.",
                "- Средний: Начальные жизни - 2, враги каждые 1,5 сек.",
                "- Сложный: Начальная жизнь - 1, враги каждый 1 сек."
            ]),
            ("Цель игры:", ["Продержитесь как можно дольше, избегайте столкновений с красными объектами."])
        ]

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            self.screen.fill((0, 0, 0))  # Черный фон

            x_offset = 100  # Отступ слева
            y_pos = 100  # Верхняя позиция начала текста

            # Вывод заголовка
            title_surface = title_font.render(help_title, True, (255, 255, 255))
            title_rect = title_surface.get_rect(topleft=(x_offset, y_pos))
            self.screen.blit(title_surface, title_rect)
            y_pos += 60  # Промежуток перед основным текстом

            # Вывод пунктов справки
            for category, details in help_lines:
                # Категория пункта
                cat_surface = content_font.render(category, True, (255, 255, 0))
                cat_rect = cat_surface.get_rect(topleft=(x_offset, y_pos))
                self.screen.blit(cat_surface, cat_rect)
                y_pos += 30  # Увеличили позицию ниже текущего блока

                # Детализация каждого пункта
                for detail in details:
                    det_surface = content_font.render(detail, True, (255, 255, 255))
                    det_rect = det_surface.get_rect(topleft=(x_offset + 20, y_pos))
                    self.screen.blit(det_surface, det_rect)
                    y_pos += 30  # Перемещаемся ниже последнего текста

            pygame.display.flip()