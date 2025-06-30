import pygame
from ui.button import Button


class SettingsScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        self.buttons = [
            Button(
                screen_width // 2 - 150, screen_height * 0.3,
                300, 50,
                "Полноэкранный режим: Вкл" if self.game.settings["fullscreen"] else "Полноэкранный режим: Выкл",
                self.toggle_fullscreen
            ),
            Button(
                screen_width // 2 - 150, screen_height * 0.4,
                300, 50,
                f"Разрешение: {self.game.settings['resolution'][0]}x{self.game.settings['resolution'][1]}",
                self.cycle_resolution
            ),
            Button(
                screen_width // 2 - 150, screen_height * 0.5,
                300, 50,
                "Применить",
                self.apply_settings
            ),
            Button(
                screen_width // 2 - 150, screen_height * 0.6,
                300, 50,
                "Назад",
                lambda: self.game.change_scene("main_menu")
            )
        ]

    def toggle_fullscreen(self):
        self.game.settings["fullscreen"] = not self.game.settings["fullscreen"]
        self.buttons[0].text = "Полноэкранный режим: Вкл" if self.game.settings[
            "fullscreen"] else "Полноэкранный режим: Выкл"

    def cycle_resolution(self):
        resolutions = [
            [800, 600],
            [1280, 720],
            [1366, 768],
            [1600, 900],
            [1920, 1080],
            [1920, 1200],
        ]

        current = self.game.settings["resolution"]
        next_index = (resolutions.index(current) + 1) % len(resolutions) if current in resolutions else 0
        self.game.settings["resolution"] = resolutions[next_index]
        self.buttons[1].text = f"Разрешение: {resolutions[next_index][0]}x{resolutions[next_index][1]}"

    def apply_settings(self):
        self.game.save_settings()
        self.game.init_screen()  # Обновляем экран
        self.game.reload_scenes()  # Пересоздаем все сцены
        self.init_ui()  # Обновляем UI настроек

    def on_enter(self):
        print("Вход в настройки")
        self.init_ui()  # Инициализируем UI при каждом входе

    def on_exit(self):
        print("Выход из настроек")

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((50, 55, 75))

        # Заголовок
        title_font = pygame.font.Font(None, 60)
        title = title_font.render("Настройки", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() * 0.15))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)
