import pygame
from menu import Menu
from app.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Космический боец")
    clock = pygame.time.Clock()

    # Экземпляр меню
    menu = Menu(screen)

    while True:
        action = menu.show_menu()  # Показываем главное меню

        if action == 'play':
            level_difficulty = menu.select_level()  # Выбор уровня сложности
            game = Game(screen, level_difficulty)
            result = game.run_game()  # Запускаем игру

            if result is not None:
                menu.records.save_record(result)  # Сохраняем результат игрока

        elif action == 'records':
            menu.show_records()  # Просмотр рекордов

        elif action == 'help':
            menu.show_help()  # Справочная страница

        elif action == 'exit':
            break  # Выход из программы

    pygame.quit()


if __name__ == "__main__":
    main()