import pygame
from ui.button import Button
from scenes.main_menu import MainMenuScene


class GameScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        self.buttons = [
            Button(
                screen_width - 210, 10,
                200, 40,
                "В главное меню",
                lambda: self.game.change_scene("main_menu")
            )
        ]

    def on_enter(self):
        print("Вход в игровую сцену")
        self.init_ui()

    def on_exit(self):
        print("Выход из игровой сцены")

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((30, 40, 50))

        # Заглушка
        font = pygame.font.Font(None, 64)
        text = font.render("Игровая сцена", True, (200, 220, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, text_rect)

        sub_font = pygame.font.Font(None, 32)
        sub_text = sub_font.render("(в разработке)", True, (180, 200, 220))
        sub_rect = sub_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
        surface.blit(sub_text, sub_rect)

        for button in self.buttons:
            button.draw(surface)
