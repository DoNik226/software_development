import pygame


class InputBox:
    def __init__(self, screen):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 200, 32)
        self.center_input_box()
        self.color_active = pygame.Color('lightskyblue3')
        self.color_passive = pygame.Color('chartreuse4')
        self.color = self.color_passive
        self.active = False
        self.text = ''
        self.font = pygame.font.SysFont(None, 32)

    def center_input_box(self):
        screen_width, _ = self.screen.get_size()
        self.rect.centerx = screen_width // 2
        self.rect.centery = self.screen.get_height() // 2

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_passive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def update(self, events):
        for event in events:
            self.handle_event(event)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(10, 10))
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)