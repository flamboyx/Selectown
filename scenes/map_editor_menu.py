import pygame
import os
import json
from ui.button import Button


class MapEditorMenuScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.map_files = []
        self.map_thumbnails = []
        self.selected_map_index = -1
        self.load_dialog_active = False
        self.load_error = ""
        self.scroll_offset = 0
        self.items_per_page = 6

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

        # Кнопки для диалога загрузки
        self.load_dialog_buttons = [
            Button(
                screen_width // 2 - 150, screen_height - 100,
                120, 40,
                "Загрузить",
                self.perform_load
            ),
            Button(
                screen_width // 2 + 30, screen_height - 100,
                120, 40,
                "Отмена",
                self.cancel_load
            ),
            Button(
                30, screen_height - 100,
                40, 40,
                "▲",
                lambda: self.scroll_maps(-1)
            ),
            Button(
                80, screen_height - 100,
                40, 40,
                "▼",
                lambda: self.scroll_maps(1)
            )
        ]

    def on_enter(self):
        print("Вход в меню редактора карт")
        self.load_dialog_active = False

    def on_exit(self):
        print("Выход из меню редактора карт")

    def handle_events(self, events):
        if self.load_dialog_active:
            for event in events:
                # Обработка кнопок диалога
                for button in self.load_dialog_buttons:
                    button.handle_event(event)

                # Обработка выбора карты
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    screen_width, screen_height = self.game.screen.get_size()

                    # Проверяем клик по миниатюрам
                    for i in range(self.scroll_offset,
                                   min(self.scroll_offset + self.items_per_page, len(self.map_files))):
                        row = (i - self.scroll_offset) // 3
                        col = (i - self.scroll_offset) % 3

                        thumb_x = 50 + col * 220
                        thumb_y = 150 + row * 120

                        thumb_rect = pygame.Rect(thumb_x, thumb_y, 200, 110)
                        if thumb_rect.collidepoint(mouse_pos):
                            self.selected_map_index = i
                            self.load_error = ""

                # Прокрутка колесом мыши
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Колесо вверх
                        self.scroll_maps(-1)
                    elif event.button == 5:  # Колесо вниз
                        self.scroll_maps(1)
            return

        # Обработка основного меню
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((40, 45, 60))

        if self.load_dialog_active:
            # Рендер диалога загрузки
            self.render_load_dialog(surface)
        else:
            # Рендер основного меню
            self.render_main_menu(surface)

    def render_main_menu(self, surface):
        """Отрисовывает главное меню редактора"""
        title_font = pygame.font.Font(None, 60)
        title = title_font.render("Редактор карт", True, (220, 240, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, surface.get_height() * 0.2))
        surface.blit(title, title_rect)

        for button in self.buttons:
            button.draw(surface)

    def render_load_dialog(self, surface):
        """Отрисовывает диалог загрузки карты"""
        screen_width, screen_height = surface.get_size()

        # Полупрозрачный фон
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Основное окно диалога
        dialog_rect = pygame.Rect(100, 100, screen_width - 200, screen_height - 200)
        pygame.draw.rect(surface, (50, 55, 75), dialog_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 110, 140), dialog_rect, 2, border_radius=10)

        # Заголовок
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("Выберите карту для загрузки", True, (220, 240, 255))
        surface.blit(title, (screen_width // 2 - title.get_width() // 2, 120))

        # Список карт
        visible_files = self.map_files[self.scroll_offset:self.scroll_offset + self.items_per_page]
        visible_thumbnails = self.map_thumbnails[self.scroll_offset:self.scroll_offset + self.items_per_page]

        for i, (map_file, thumbnail) in enumerate(zip(visible_files, visible_thumbnails)):
            row = i // 3
            col = i % 3

            thumb_x = 120 + col * 220
            thumb_y = 180 + row * 120

            # Подсветка выбранной карты
            if self.selected_map_index == i + self.scroll_offset:
                pygame.draw.rect(surface, (100, 200, 255),
                                 (thumb_x - 5, thumb_y - 5, 190, 110), 3, border_radius=5)

            # Миниатюра карты
            surface.blit(thumbnail, (thumb_x, thumb_y))

            # Название файла
            font = pygame.font.Font(None, 20)
            name_text = font.render(os.path.splitext(map_file)[0], True, (200, 200, 200))
            surface.blit(name_text, (thumb_x + 10, thumb_y + 105))

        # Информация о прокрутке
        scroll_info = f"Карты {self.scroll_offset + 1}-{min(self.scroll_offset + self.items_per_page, len(self.map_files))} из {len(self.map_files)}"
        info_text = font.render(scroll_info, True, (200, 200, 200))
        surface.blit(info_text, (120, screen_height - 150))

        # Сообщение об ошибке
        if self.load_error:
            error_font = pygame.font.Font(None, 26)
            error_text = error_font.render(self.load_error, True, (255, 100, 100))
            surface.blit(error_text, (screen_width // 2 - error_text.get_width() // 2, 150))

        # Кнопки диалога
        for button in self.load_dialog_buttons:
            button.draw(surface)

    def get_map_files(self):
        """Возвращает список доступных карт"""
        if not os.path.exists("maps"):
            return []
        return [f for f in os.listdir("maps") if f.endswith('.json')]

    def prepare_map_previews(self):
        """Создаёт миниатюры для карт"""
        self.map_thumbnails = []

        for map_file in self.map_files:
            # здесь можно генерировать превью из содержимого карты
            preview = pygame.Surface((180, 100))
            color = (50, 100, 150)  # Заглушка - цвет фона
            preview.fill(color)

            # Добавляем название файла
            font = pygame.font.Font(None, 20)
            text = font.render(os.path.splitext(map_file)[0], True, (255, 255, 255))
            text_rect = text.get_rect(center=(90, 20))
            preview.blit(text, text_rect)

            self.map_thumbnails.append(preview)

    def scroll_maps(self, direction):
        """Прокручивает список карт"""
        max_offset = max(0, len(self.map_files) - self.items_per_page)
        self.scroll_offset = max(0, min(max_offset, self.scroll_offset + direction))

    def load_map_dialog(self):
        """Активирует диалог загрузки карты"""
        self.load_dialog_active = True
        self.map_files = self.get_map_files()
        self.selected_map_index = -1
        self.scroll_offset = 0
        self.load_error = ""
        self.prepare_map_previews()

    def perform_load(self):
        """Загружает выбранную карту"""
        if self.selected_map_index == -1:
            self.load_error = "Выберите карту для загрузки!"
            return

        filepath = os.path.join("maps", self.map_files[self.selected_map_index])

        # Передаём параметр загрузки в редактор
        self.game.editor_params = {
            "load_file": filepath
        }

        # Переходим в редактор
        self.game.change_scene("map_editor")
        self.load_dialog_active = False

    def cancel_load(self):
        """Закрывает диалог загрузки"""
        self.load_dialog_active = False

    def load_map(self, filename):
        """Загружает карту и переходит в редактор"""
        try:
            # Сохраняем имя файла в game для передачи в редактор
            self.game.editor_params = {
                "load_file": os.path.join("maps", filename)
            }

            # Переходим в редактор карт
            self.game.change_scene("map_editor")

        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.load_error = f"Ошибка загрузки: {str(e)}"


