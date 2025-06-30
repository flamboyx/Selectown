import pygame
import time
from ui.button import Button
from ui.dropdown import Dropdown


class MapEditorParamsScene:
    def __init__(self, game):
        self.game = game
        self.size_dropdown = None
        self.terrain_dropdown = None
        self.create_button = None
        self.back_button = None
        self.last_dropdown_action_time = 0
        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        # Варианты размеров карты
        size_options = [
            "Миниатюрная (32x32)",
            "Маленькая (48x48)",
            "Средняя (64x64)",
            "Большая (96x96)",
            "Огромная (128x128)",
            "Гигантская (256x256)"
        ]

        # Варианты типов поверхности
        terrain_options = ["Трава", "Песок", "Земля", "Лес", "Вода"]

        # Выпадающий список для размера
        self.size_dropdown = Dropdown(
            x=screen_width // 2 - 150,
            y=200,
            width=300,
            height=40,
            options=size_options,
            default_index=2
        )

        # Выпадающий список для типа поверхности
        self.terrain_dropdown = Dropdown(
            x=screen_width // 2 - 150,
            y=300,
            width=300,
            height=40,
            options=terrain_options,
            default_index=0
        )

        # Устанавливаем z-index
        self.size_dropdown.set_z_index(1)
        self.terrain_dropdown.set_z_index(2)

        # Кнопка создания карты
        self.create_button = Button(
            screen_width // 2 - 100,
            400,
            200, 50,
            "Создать",
            self.create_map
        )

        # Кнопка назад
        self.back_button = Button(
            20, screen_height - 60,
            150, 40,
            "Назад",
            lambda: self.game.change_scene("map_editor_menu")
        )

    def create_map(self):
        current_time = time.time()
        if current_time - self.last_dropdown_action_time < 0.3:
            return

        size_option = self.size_dropdown.get_selected()
        terrain_option = self.terrain_dropdown.get_selected()

        size_map = {
            "Миниатюрная (32x32)": 32,
            "Маленькая (48x48)": 48,
            "Средняя (64x64)": 64,
            "Большая (96x96)": 96,
            "Огромная (128x128)": 128,
            "Гигантская (256x256)": 256
        }

        terrain_map = {
            "Трава": "grass",
            "Песок": "sand",
            "Земля": "earth",
            "Лес": "forest",
            "Вода": "water"
        }

        self.game.editor_params = {
            "size": size_map[size_option],
            "terrain": terrain_map[terrain_option]
        }

        self.game.change_scene("map_editor")

    def on_enter(self):
        print("Выбор параметров карты")
        self.last_dropdown_action_time = 0

    def on_exit(self):
        print("Выход из выбора параметров")

    def handle_events(self, events):
        current_time = time.time()
        dropdown_interaction = False

        for event in events:
            # Обработка только релевантных событий (мыши и клавиатуры)
            if event.type not in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.KEYDOWN]:
                continue

            # Закрытие других списков при открытии одного
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.size_dropdown.rect.collidepoint(event.pos):
                    self.terrain_dropdown.is_open = False
                elif self.terrain_dropdown.rect.collidepoint(event.pos):
                    self.size_dropdown.is_open = False

            # Обработка событий для выпадающих списков
            if self.size_dropdown.handle_event(event):
                self.last_dropdown_action_time = current_time
                dropdown_interaction = True

            if self.terrain_dropdown.handle_event(event):
                self.last_dropdown_action_time = current_time
                dropdown_interaction = True

        # Обработка кнопок
        if not dropdown_interaction and current_time - self.last_dropdown_action_time > 0.3:
            for event in events:
                self.create_button.handle_event(event)
                self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((50, 55, 75))

        # Заголовок
        title_font = pygame.font.Font(None, 60)
        title = title_font.render("Параметры карты", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)

        # Подписи
        font = pygame.font.Font(None, 36)
        size_label = font.render("Размер карты:", True, (200, 200, 200))
        terrain_label = font.render("Тип поверхности:", True, (200, 200, 200))
        surface.blit(size_label, (surface.get_width() // 2 - 150, 160))
        surface.blit(terrain_label, (surface.get_width() // 2 - 150, 260))

        # Отрисовка кнопок
        self.create_button.draw(surface)
        self.back_button.draw(surface)

        # Отрисовка закрытых состояний выпадающих списков
        self.size_dropdown.draw_closed(surface)
        self.terrain_dropdown.draw_closed(surface)

        # Отрисовка открытых состояний поверх всего
        self.size_dropdown.draw_open(surface)
        self.terrain_dropdown.draw_open(surface)
