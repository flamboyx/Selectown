import pygame
from ui.button import Button


class MainMenuScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.background = pygame.Surface(game.screen.get_size())
        self.background.fill((40, 45, 60))

        # Создание градиента
        for y in range(self.background.get_height()):
            color_val = 60 - int(y / self.background.get_height() * 20)
            pygame.draw.line(
                self.background,
                (40, color_val, 80),
                (0, y),
                (self.background.get_width(), y)
            )

        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()
        button_width, button_height = 300, 60
        button_x = (screen_width - button_width) // 2

        self.buttons = [
            Button(
                button_x, screen_height * 0.4,
                button_width, button_height,
                "Новая игра",
                lambda: self.game.change_scene("map_select")
            ),
            Button(
                button_x, screen_height * 0.5,
                button_width, button_height,
                "Загрузить игру",
                lambda: print("Загрузить игру")
            ),
            Button(
                button_x, screen_height * 0.6,
                button_width, button_height,
                "Редактор карт",
                lambda: self.game.change_scene("map_editor_menu")
            ),
            Button(
                button_x, screen_height * 0.7,
                button_width, button_height,
                "Настройки",
                lambda: self.game.change_scene("settings")
            ),
            Button(
                button_x, screen_height * 0.8,
                button_width, button_height,
                "Выход",
                self.game.quit
            ),
        ]

    def on_enter(self):
        print("Вход в главное меню")
        self.init_ui()

    def on_exit(self):
        print("Выход из главного меню")

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.blit(self.background, (0, 0))

        # Заголовок игры
        title_font = pygame.font.Font(None, 80)
        title = title_font.render("Selectown", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() * 0.2))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)
