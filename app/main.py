import pygame
from menu import Menu
from app.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Космический боец")
    clock = pygame.time.Clock()

    menu = Menu(screen)

    while True:
        action = menu.show_menu()

        if action == 'play':
            level_difficulty = menu.select_level()
            game = Game(screen, level_difficulty)
            result = game.run_game()

            if result is not None:
                menu.records.save_record(result)

        elif action == 'records':
            menu.show_records()

        elif action == 'help':
            menu.show_help()

        elif action == 'exit':
            break

    pygame.quit()


if __name__ == "__main__":
    main()