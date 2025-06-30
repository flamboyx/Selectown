import pygame
from ui.button import Button


class MapEditorMenuScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        # Кнопки меню редактора
        btn_width, btn_height = 300, 60
        start_x = (screen_width - btn_width) // 2
        start_y = (screen_height - 3 * (btn_height + 20)) // 2

        self.buttons = [
            Button(
                start_x, start_y,
                btn_width, btn_height,
                "Создать карту",
                lambda: self.game.change_scene("map_editor_params")  # Переход к параметрам
            ),
            Button(
                start_x, start_y + btn_height + 20,
                btn_width, btn_height,
                "Загрузить карту",
                self.load_map_dialog
            ),
            Button(
                start_x, start_y + 2 * (btn_height + 20),
                btn_width, btn_height,
                "Главное меню",
                lambda: self.game.change_scene("main_menu")
            )
        ]

    def on_enter(self):
        print("Вход в меню редактора карт")

    def on_exit(self):
        print("Выход из меню редактора карт")

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((40, 45, 60))

        # Заголовок
        title_font = pygame.font.Font(None, 60)
        title = title_font.render("Редактор карт", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() * 0.2))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

    def load_map_dialog(self):
        # Заглушка для диалога загрузки
        print("Загрузка карты (заглушка)")
