import pygame
from ui.button import Button
from scenes.main_menu import MainMenuScene


class MapSelectScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        # Кнопки выбора карты
        map_button_size = 180
        spacing = 40
        total_width = 3 * map_button_size + 2 * spacing
        start_x = (screen_width - total_width) // 2

        self.buttons = [
            Button(
                start_x, screen_height * 0.3,
                map_button_size, map_button_size,
                "Карта 1",
                lambda: self.game.change_scene("game")
            ),
            Button(
                start_x + map_button_size + spacing, screen_height * 0.3,
                map_button_size, map_button_size,
                "Карта 2",
                lambda: self.game.change_scene("game")
            ),
            Button(
                start_x + 2 * (map_button_size + spacing), screen_height * 0.3,
                map_button_size, map_button_size,
                "Случайная",
                lambda: self.game.change_scene("game")
            ),
            Button(
                screen_width // 2 - 100, screen_height * 0.8,
                200, 50,
                "Назад",
                lambda: self.game.change_scene("main_menu")
            )
        ]

    def on_enter(self):
        print("Вход в выбор карты")
        self.init_ui()

    def on_exit(self):
        print("Выход из выбора карты")

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((45, 50, 70))

        # Заголовок
        title_font = pygame.font.Font(None, 60)
        title = title_font.render("Выбор карты", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() * 0.15))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

        # Подписи карт
        font = pygame.font.Font(None, 28)
        texts = ["Лесная долина", "Пустынный каньон", "Случайная генерация"]
        for i, text in enumerate(texts):
            text_surf = font.render(text, True, (200, 200, 200))
            text_rect = text_surf.get_rect(
                center=(self.buttons[i].rect.centerx, self.buttons[i].rect.bottom + 20)
            )
            surface.blit(text_surf, text_rect)
