import pygame
import json
import os
import re
from ui.button import Button
from ui.slider import Slider
from world.map import Map


class MapEditorScene:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.tile_buttons = []
        self.tool_buttons = []
        self.tile_types = {
            'grass': (50, 200, 50),
            'sand': (230, 220, 100),
            'earth': (150, 100, 50),
            'forest': (0, 150, 0),
            'water': (0, 100, 200)
        }
        self.default_tile = 'grass'
        self.current_tile_type = 'grass'
        self.current_tool = 'brush'
        self.dragging = False
        self.drag_start_x, self.drag_start_y = 0, 0
        self.map = None
        self.show_load_dialog = None

        self.save_dialog_active = False
        self.filename_input = ""
        self.input_rect = None
        self.save_dialog_buttons = []
        self.error_message = ""
        self.input_active = False
        self.last_blink_time = 0
        self.cursor_visible = True

        self.load_dialog_active = False
        self.map_files = []
        self.selected_map_index = -1
        self.map_thumbnails = []
        self.load_dialog_buttons = []
        self.load_error = ""
        self.scroll_offset = 0
        self.items_per_page = 6

        self.init_ui()

    def init_ui(self):
        screen_width, screen_height = self.game.screen.get_size()

        # Кнопки для выбора типа тайла
        tile_btn_size = 40
        spacing = 10
        start_x = 20
        start_y = screen_height - tile_btn_size - 20

        self.tile_buttons = []
        for i, (tile_name, tile_color) in enumerate(self.tile_types.items()):
            self.tile_buttons.append({
                'rect': pygame.Rect(start_x + i * (tile_btn_size + spacing), start_y, tile_btn_size, tile_btn_size),
                'name': tile_name,
                'color': tile_color
            })

        # Кнопки инструментов
        self.tool_buttons = [
            {
                'rect': pygame.Rect(start_x + len(self.tile_types) * (tile_btn_size + spacing) + 20, start_y,
                                    tile_btn_size, tile_btn_size),
                'name': 'brush',
                'color': (200, 200, 200),
                'label': 'Кисть'
            },
            {
                'rect': pygame.Rect(start_x + len(self.tile_types) * (tile_btn_size + spacing) + tile_btn_size + 30,
                                    start_y, tile_btn_size, tile_btn_size),
                'name': 'eraser',
                'color': (150, 150, 150),
                'label': 'Ластик'
            },
            {
                'rect': pygame.Rect(
                    start_x + len(self.tile_types) * (tile_btn_size + spacing) + 2 * (tile_btn_size + 10), start_y,
                    tile_btn_size, tile_btn_size),
                'name': 'fill',
                'color': (100, 100, 200),
                'label': 'Заливка'
            }
        ]

        # Кнопки управления
        self.buttons = [
            Button(
                screen_width - 210, 10,
                200, 40,
                "Сохранить",
                self.save_map
            ),
            Button(
                screen_width - 210, 60,
                200, 40,
                "Загрузить",
                self.load_map_dialog
            ),
            Button(
                screen_width - 210, 110,
                200, 40,
                "Назад",
                lambda: self.game.change_scene("map_editor_menu")
            )
        ]

        # Слайдер для размера кисти
        self.brush_slider = Slider(
            x=screen_width - 250,
            y=160,
            width=180,
            height=20,
            min_val=1,
            max_val=32,
            initial_val=1,
            label="Размер кисти"
        )

        # Кнопка переключения сетки
        self.grid_button = Button(
            screen_width - 210, 160,
            200, 40,
            "Сетка: ВКЛ",
            self.toggle_grid
        )
        self.buttons.append(self.grid_button)

        # Инициализация UI для диалогов
        self.init_save_dialog_ui()
        self.init_load_dialog_ui()

    def on_enter(self):
        print("Вход в редактор карт")

        # Загрузка параметров из game
        if hasattr(self.game, 'editor_params'):
            # Если есть файл для загрузки
            if 'load_file' in self.game.editor_params:
                self.load_map(self.game.editor_params['load_file'])
            # Или параметры создания новой карты
            elif 'size' in self.game.editor_params:
                size = self.game.editor_params.get('size', 64)
                terrain = self.game.editor_params.get('terrain', 'grass')
                self.create_map(size, terrain)

            del self.game.editor_params  # Очищаем параметры
        else:
            # По умолчанию создаем карту 64x64
            self.create_map(64, 'grass')

    def create_map(self, size, terrain='grass'):
        """Создает новую карту заданного размера и типа"""
        self.map = Map(size, size, terrain)
        print(f"Создана новая карта {size}x{size} с типом поверхности: {terrain}")

    def on_exit(self):
        print("Выход из редактора карт")

    def handle_events(self, events):
        if self.map is None:
            return

        # Флаг для отслеживания взаимодействия с UI
        ui_interaction = False

        for event in events:
            # Если активен диалог сохранения - обрабатываем только его
            if self.save_dialog_active:
                for button in self.save_dialog_buttons:
                    button.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.input_rect.collidepoint(event.pos):
                        self.input_active = True
                        self.last_blink_time = pygame.time.get_ticks()
                        self.cursor_visible = True
                    else:
                        self.input_active = False

                if event.type == pygame.KEYDOWN and self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.perform_save()
                    elif event.key == pygame.K_ESCAPE:
                        self.cancel_save()
                    elif event.key == pygame.K_BACKSPACE:
                        self.filename_input = self.filename_input[:-1]
                        self.error_message = ""
                    else:
                        # Ограничение длины имени файла
                        if len(self.filename_input) < 30:
                            self.filename_input += event.unicode
                            self.error_message = ""

                return

            # Если активен диалог загрузки - обрабатываем только его
            if self.load_dialog_active:
                for button in self.load_dialog_buttons:
                    button.handle_event(event)

                # Обработка клика по миниатюрам карт
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    screen_width, screen_height = self.game.screen.get_size()
                    dialog_width, dialog_height = 700, 500
                    dialog_x = (screen_width - dialog_width) // 2
                    dialog_y = (screen_height - dialog_height) // 2

                    # Проверяем клик по миниатюрам
                    for i in range(self.scroll_offset,
                                   min(self.scroll_offset + self.items_per_page, len(self.map_files))):
                        row = (i - self.scroll_offset) // 3
                        col = (i - self.scroll_offset) % 3

                        thumb_x = dialog_x + 20 + col * 220
                        thumb_y = dialog_y + 60 + row * 120

                        thumb_rect = pygame.Rect(thumb_x, thumb_y, 200, 110)
                        if thumb_rect.collidepoint(mouse_pos):
                            self.selected_map_index = i
                            self.load_error = ""

                # Обработка колесика мыши для прокрутки
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Колесо вверх
                        self.scroll_maps(-1)
                    elif event.button == 5:  # Колесо вниз
                        self.scroll_maps(1)

                return

            # Обработка UI элементов в первую очередь
            ui_handled = False

            # Обработка основных кнопок
            for button in self.buttons:
                if button.handle_event(event):
                    ui_handled = True
                    ui_interaction = True

            # Обработка слайдера
            if self.brush_slider.handle_event(event):
                ui_handled = True
                ui_interaction = True

            # Обработка кнопок выбора тайлов и инструментов
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.tile_buttons:
                    if btn['rect'].collidepoint(event.pos):
                        self.current_tile_type = btn['name']
                        ui_handled = True
                        ui_interaction = True

                for btn in self.tool_buttons:
                    if btn['rect'].collidepoint(event.pos):
                        self.current_tool = btn['name']
                        ui_handled = True
                        ui_interaction = True

            # Если событие обработано UI, пропускаем обработку карты
            if ui_handled:
                continue

            # Обработка событий карты
            # Обработка перемещения камеры
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка
                    # Проверка, что клик не на UI
                    if not self.is_point_on_ui(event.pos):
                        self.handle_mouse_click(event.pos)
                elif event.button == 2:  # Средняя кнопка - перетаскивание
                    self.dragging = True
                    self.drag_start_x, self.drag_start_y = event.pos
                elif event.button == 4:  # Колесо вверх - масштаб+
                    self.map.zoom_in()
                elif event.button == 5:  # Колесо вниз - масштаб-
                    self.map.zoom_out()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.map.camera_x -= dx
                    self.map.camera_y -= dy
                    self.drag_start_x, self.drag_start_y = event.pos
                elif pygame.mouse.get_pressed()[0]:  # ЛКМ зажата
                    # Проверка, что курсор не на UI
                    if not self.is_point_on_ui(event.pos):
                        if self.current_tool == 'brush':
                            self.handle_paint(event.pos)
                        elif self.current_tool == 'eraser':
                            self.handle_erase(event.pos)

            # Обработка клавиатуры
            if event.type == pygame.KEYDOWN:
                # Shift+G - смена цвета сетки
                if event.key == pygame.K_g and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.map.toggle_grid_color()

                # Ctrl+G - смена стиля сетки
                elif event.key == pygame.K_g and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.map.toggle_grid_style()

                # Клавиша G - переключение сетки
                elif event.key == pygame.K_g:
                    self.map.show_grid = not self.map.show_grid
                    self.grid_button.text = f"Сетка: {'ВКЛ' if self.map.show_grid else 'ВЫКЛ'}"
                    print(f"Сетка {'включена' if self.map.show_grid else 'выключена'}")

            # Обработка краев экрана для плавного перемещения
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen_width, screen_height = self.game.screen.get_size()
            move_speed = 5

            # Проверка, что курсор не на UI при обработке краёв экрана
            if not self.is_point_on_ui((mouse_x, mouse_y)):
                if mouse_x < 20:
                    self.map.camera_x -= move_speed
                elif mouse_x > screen_width - 20:
                    self.map.camera_x += move_speed

                if mouse_y < 20:
                    self.map.camera_y -= move_speed
                elif mouse_y > screen_height - 20:
                    self.map.camera_y += move_speed

            # Обработка слайдера (повторно, для обновления значения)
            if hasattr(self, 'map'):
                self.map.brush_size = int(self.brush_slider.get_value())

        # Сбрасываем флаг взаимодействия с UI после обработки всех событий
        self.ui_interaction = ui_interaction

    def is_point_on_ui(self, pos):
        """Проверяет, находится ли точка на любом UI-элементе"""
        # Проверка основных кнопок
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return True

        # Проверка кнопок выбора тайлов
        for btn in self.tile_buttons:
            if btn['rect'].collidepoint(pos):
                return True

        # Проверка кнопок инструментов
        for btn in self.tool_buttons:
            if btn['rect'].collidepoint(pos):
                return True

        # Проверка слайдера
        if self.brush_slider.rect.collidepoint(pos):
            return True

        return False

    def handle_mouse_click(self, mouse_pos):
        """Обработка клика мыши в зависимости от выбранного инструмента"""
        # Рассчитываем координаты тайла с учетом камеры
        tile_x = (mouse_pos[0] + self.map.camera_x) // self.map.tile_size
        tile_y = (mouse_pos[1] + self.map.camera_y) // self.map.tile_size

        if self.current_tool == 'brush':
            self.map.set_tiles_area(tile_x, tile_y, self.map.brush_size, self.current_tile_type)
        elif self.current_tool == 'eraser':
            self.map.set_tiles_area(tile_x, tile_y, self.map.brush_size, self.map.default_tile)
        elif self.current_tool == 'fill':
            target_tile = self.map.get_tile(tile_x, tile_y)
            if target_tile:
                self.map.fill_area(tile_x, tile_y, target_tile, self.current_tile_type)

    def handle_paint(self, pos):
        """Обработка рисования при зажатой ЛКМ"""
        if self.current_tool == 'brush':
            tile_x = (pos[0] + self.map.camera_x) // self.map.tile_size
            tile_y = (pos[1] + self.map.camera_y) // self.map.tile_size
            self.map.set_tiles_area(tile_x, tile_y, self.map.brush_size, self.current_tile_type)

    def handle_erase(self, pos):
        """Обработка стирания при зажатой ЛКМ"""
        if self.current_tool == 'eraser':
            tile_x = (pos[0] + self.map.camera_x) // self.map.tile_size
            tile_y = (pos[1] + self.map.camera_y) // self.map.tile_size
            self.map.set_tiles_area(tile_x, tile_y, self.map.brush_size, self.map.default_tile)

    def update(self, dt):
        pass

    def render(self, surface):
        if self.map is None:
            surface.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render("Загрузка...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
            surface.blit(text, text_rect)
            return

        surface.fill((0, 0, 0))  # Черный фон за картой

        # Рендер карты
        for y in range(self.map.height):
            for x in range(self.map.width):
                tile_type = self.map.get_tile(x, y)
                color = self.tile_types.get(tile_type, (100, 100, 100))

                # Рассчитываем позицию с учетом камеры и масштаба
                rect_x = x * self.map.tile_size - self.map.camera_x
                rect_y = y * self.map.tile_size - self.map.camera_y

                # Рисуем только видимые тайлы
                if (rect_x + self.map.tile_size > 0 and rect_x < surface.get_width() and
                        rect_y + self.map.tile_size > 0 and rect_y < surface.get_height()):
                    pygame.draw.rect(
                        surface,
                        color,
                        (rect_x, rect_y, self.map.tile_size, self.map.tile_size)
                    )

        # Предпросмотр области рисования - только если нет взаимодействия с UI
        if (self.current_tool in ['brush', 'eraser'] and
                pygame.mouse.get_pressed()[0] and
                not self.ui_interaction and
                not self.is_point_on_ui(pygame.mouse.get_pos())):

            mouse_pos = pygame.mouse.get_pos()
            tile_x = (mouse_pos[0] + self.map.camera_x) // self.map.tile_size
            tile_y = (mouse_pos[1] + self.map.camera_y) // self.map.tile_size

            # Рисуем полупрозрачный круг для предпросмотра
            preview_surface = pygame.Surface((self.map.tile_size, self.map.tile_size), pygame.SRCALPHA)
            color = (100, 200, 255, 100) if self.current_tool == 'brush' else (255, 100, 100, 100)
            pygame.draw.circle(preview_surface, color,
                               (self.map.tile_size // 2, self.map.tile_size // 2),
                               self.map.tile_size // 2)

            for y in range(-self.map.brush_size, self.map.brush_size + 1):
                for x in range(-self.map.brush_size, self.map.brush_size + 1):
                    if x * x + y * y <= self.map.brush_size * self.map.brush_size:
                        screen_x = (tile_x + x) * self.map.tile_size - self.map.camera_x
                        screen_y = (tile_y + y) * self.map.tile_size - self.map.camera_y
                        surface.blit(preview_surface, (screen_x, screen_y))

        # Рендер сетки поверх тайлов
        self.map.draw_grid(surface, self.map.camera_x, self.map.camera_y)

        # Рендер UI поверх карты
        for button in self.buttons:
            button.draw(surface)

        # Рендер кнопок выбора тайла
        for btn in self.tile_buttons:
            pygame.draw.rect(surface, btn['color'], btn['rect'])
            # Подсветка выбранного типа
            if btn['name'] == self.current_tile_type:
                pygame.draw.rect(surface, (255, 255, 0), btn['rect'], 3)

        # Рендер кнопок инструментов
        for btn in self.tool_buttons:
            pygame.draw.rect(surface, btn['color'], btn['rect'])
            # Подсветка выбранного инструмента
            if btn['name'] == self.current_tool:
                pygame.draw.rect(surface, (255, 255, 0), btn['rect'], 3)

        # Рендер слайдера
        self.brush_slider.draw(surface)

        # Отображение информации о текущем инструменте и состоянии сетки
        font = pygame.font.Font(None, 24)
        grid_status = "ВКЛ" if self.map.show_grid else "ВЫКЛ"
        info_text = f"Инструмент: {self.current_tool} | Размер: {self.map.brush_size} | Тайл: {self.current_tile_type} | Сетка: {grid_status}"
        text_surf = font.render(info_text, True, (255, 255, 255))
        surface.blit(text_surf, (20, 20))

        # Рендер диалога сохранения поверх всего
        if self.save_dialog_active:
            # Полупрозрачный фон
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

            # Основной прямоугольник диалога
            dialog_width, dialog_height = 500, 200
            dialog_x = (surface.get_width() - dialog_width) // 2
            dialog_y = (surface.get_height() - dialog_height) // 2
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

            pygame.draw.rect(surface, (50, 55, 75), dialog_rect, border_radius=10)
            pygame.draw.rect(surface, (100, 110, 140), dialog_rect, 2, border_radius=10)

            # Заголовок
            title_font = pygame.font.Font(None, 36)
            title = title_font.render("Сохранить карту", True, (220, 240, 255))
            surface.blit(title, (dialog_x + 20, dialog_y + 10))

            # Текст подсказки
            font = pygame.font.Font(None, 28)
            prompt = font.render("Введите имя файла:", True, (200, 200, 200))
            surface.blit(prompt, (dialog_x + 20, dialog_y + 50))

            # Поле ввода
            pygame.draw.rect(surface, (30, 35, 45), self.input_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 150, 200) if self.input_active else (70, 90, 120),
                             self.input_rect, 2, border_radius=5)

            # Введенный текст
            input_font = pygame.font.Font(None, 32)
            input_text = input_font.render(self.filename_input, True, (255, 255, 255))
            surface.blit(input_text, (self.input_rect.x + 10, self.input_rect.y + 8))

            # Мигающий курсор
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time > 500:  # 500ms
                self.cursor_visible = not self.cursor_visible
                self.last_blink_time = current_time

            if self.input_active and self.cursor_visible:
                cursor_x = self.input_rect.x + 10 + input_text.get_width()
                pygame.draw.line(surface, (255, 255, 255),
                                 (cursor_x, self.input_rect.y + 5),
                                 (cursor_x, self.input_rect.y + self.input_rect.height - 5),
                                 2)

            # Сообщение об ошибке
            if self.error_message:
                error_font = pygame.font.Font(None, 26)
                error_text = error_font.render(self.error_message, True, (255, 100, 100))
                surface.blit(error_text, (dialog_x + 20, dialog_y + 100))

            # Кнопки диалога
            for button in self.save_dialog_buttons:
                button.draw(surface)

        # Рендер диалога загрузки поверх всего
        if self.load_dialog_active:
            # Полупрозрачный фон
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))

            # Основной прямоугольник диалога
            dialog_width, dialog_height = 700, 500
            dialog_x = (surface.get_width() - dialog_width) // 2
            dialog_y = (surface.get_height() - dialog_height) // 2
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

            pygame.draw.rect(surface, (50, 55, 75), dialog_rect, border_radius=10)
            pygame.draw.rect(surface, (100, 110, 140), dialog_rect, 2, border_radius=10)

            # Заголовок
            title_font = pygame.font.Font(None, 36)
            title = title_font.render("Загрузить карту", True, (220, 240, 255))
            surface.blit(title, (dialog_x + 20, dialog_y + 10))

            # Список доступных карт
            font = pygame.font.Font(None, 24)

            # Отображаем карты с текущим смещением
            visible_files = self.map_files[self.scroll_offset:self.scroll_offset + self.items_per_page]
            visible_thumbnails = self.map_thumbnails[
                                 self.scroll_offset:self.scroll_offset + self.items_per_page]

            for i, (map_file, thumbnail) in enumerate(zip(visible_files, visible_thumbnails)):
                row = i // 3
                col = i % 3

                thumb_x = dialog_x + 20 + col * 220
                thumb_y = dialog_y + 60 + row * 120

                # Рамка для выбранной карты
                if self.selected_map_index == i + self.scroll_offset:
                    pygame.draw.rect(surface, (100, 200, 255),
                                     (thumb_x - 5, thumb_y - 5, 210, 120), 3, border_radius=5)

                # Миниатюра карты
                surface.blit(thumbnail, (thumb_x, thumb_y))

                # Название файла
                name_font = pygame.font.Font(None, 20)
                name_text = name_font.render(os.path.splitext(map_file)[0], True, (200, 200, 200))
                surface.blit(name_text, (thumb_x + 5, thumb_y + 102))

            # Информация о прокрутке
            scroll_info = f"Карты {self.scroll_offset + 1}-{min(self.scroll_offset + self.items_per_page, len(self.map_files))} из {len(self.map_files)}"
            info_text = font.render(scroll_info, True, (200, 200, 200))
            surface.blit(info_text, (dialog_x + 120, dialog_y + dialog_height - 50))

            # Сообщение об ошибке
            if self.load_error:
                error_font = pygame.font.Font(None, 26)
                error_text = error_font.render(self.load_error, True, (255, 100, 100))
                surface.blit(error_text, (dialog_x + 20, dialog_y + 25))

            # Кнопки диалога
            for button in self.load_dialog_buttons:
                button.draw(surface)

    def init_save_dialog_ui(self):
        """Инициализирует UI для диалога сохранения"""
        screen_width, screen_height = self.game.screen.get_size()

        # Центральный прямоугольник диалога
        dialog_width, dialog_height = 500, 200
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Поле ввода
        input_width, input_height = 400, 40
        self.input_rect = pygame.Rect(
            dialog_x + (dialog_width - input_width) // 2,
            dialog_y + 50,
            input_width,
            input_height
        )

        # Кнопки диалога
        btn_width, btn_height = 120, 40
        self.save_dialog_buttons = [
            Button(
                dialog_x + (dialog_width - btn_width * 2 - 20) // 2,
                dialog_y + 120,
                btn_width, btn_height,
                "Сохранить",
                self.perform_save
            ),
            Button(
                dialog_x + (dialog_width - btn_width * 2 - 20) // 2 + btn_width + 20,
                dialog_y + 120,
                btn_width, btn_height,
                "Отмена",
                self.cancel_save
            )
        ]

    def save_map(self):
        """Активирует диалог сохранения вместо немедленного сохранения"""
        self.save_dialog_active = True
        self.filename_input = ""
        self.error_message = ""
        self.input_active = True
        self.last_blink_time = pygame.time.get_ticks()
        self.cursor_visible = True

    def perform_save(self):
        """Выполняет сохранение карты с введенным именем"""
        if not self.filename_input:
            self.error_message = "Имя файла не может быть пустым!"
            return

        # Очистка имени файла от недопустимых символов
        cleaned_name = re.sub(r'[^\w\-_]', '', self.filename_input)
        if not cleaned_name:
            self.error_message = "Недопустимое имя файла!"
            return

        filename = f"{cleaned_name}.json"
        filepath = os.path.join("maps", filename)

        # Проверка, не существует ли файл
        if os.path.exists(filepath):
            self.error_message = "Файл с таким именем уже существует!"
            return

        # Сохранение карты
        map_info = {
            'size': self.map.width,
            'tiles': self.map.tiles,
            'default_tile': self.map.default_tile
        }

        os.makedirs("maps", exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(map_info, f, indent=4)

        print(f"Карта сохранена как {filename}")
        self.save_dialog_active = False

    def cancel_save(self):
        """Отменяет сохранение и закрывает диалог"""
        self.save_dialog_active = False

    def init_load_dialog_ui(self):
        """Инициализирует UI для диалога загрузки"""
        screen_width, screen_height = self.game.screen.get_size()

        # Центральный прямоугольник диалога
        dialog_width, dialog_height = 700, 500
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Кнопки диалога
        btn_width, btn_height = 120, 40
        self.load_dialog_buttons = [
            Button(
                dialog_x + (dialog_width - btn_width * 2 - 20) // 2,
                dialog_y + dialog_height - 60,
                btn_width, btn_height,
                "Загрузить",
                self.perform_load
            ),
            Button(
                dialog_x + (dialog_width - btn_width * 2 - 20) // 2 + btn_width + 20,
                dialog_y + dialog_height - 60,
                btn_width, btn_height,
                "Отмена",
                self.cancel_load
            ),
            Button(
                dialog_x + 20,
                dialog_y + dialog_height - 60,
                40, btn_height,
                "▲",
                lambda: self.scroll_maps(-1)
            ),
            Button(
                dialog_x + 70,
                dialog_y + dialog_height - 60,
                40, btn_height,
                "▼",
                lambda: self.scroll_maps(1)
            )
        ]

    def load_map_dialog(self):
        """Активирует диалог загрузки карты"""
        self.load_dialog_active = True
        self.map_files = self.get_map_files()
        self.selected_map_index = -1
        self.scroll_offset = 0
        self.load_error = ""
        self.prepare_map_previews()

    def load_map(self, filepath):
        """Загружает карту из файла с улучшениями"""
        try:
            with open(filepath, 'r') as f:
                map_info = json.load(f)

            # Создаем новую карту
            size = map_info['size']
            default_tile = map_info.get('default_tile', 'grass')
            self.map = Map(size, size, default_tile)
            self.map.tiles = map_info['tiles']

            # Сбрасываем параметры камеры
            self.map.camera_x = 0
            self.map.camera_y = 0
            self.map.tile_size = 24  # Сброс масштаба

            print(f"Карта {os.path.basename(filepath)} загружена")
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            self.load_error = f"Ошибка загрузки: {str(e)}"
            # Создаем новую карту при ошибке
            self.create_map(64, 'grass')

    def perform_load(self):
        """Загружает выбранную карту"""
        if self.selected_map_index == -1:
            self.load_error = "Выберите карту для загрузки!"
            return

        filepath = os.path.join("maps", self.map_files[self.selected_map_index])
        self.load_map(filepath)
        self.load_dialog_active = False

    def cancel_load(self):
        """Отменяет загрузку и закрывает диалог"""
        self.load_dialog_active = False

    def prepare_map_previews(self):
        """Создает миниатюры для карт"""
        self.map_thumbnails = []

        # В реальном проекте здесь можно было бы генерировать превью,
        # но пока будем использовать заглушки
        for i, map_file in enumerate(self.map_files):
            # Создаем поверхность для миниатюры
            preview = pygame.Surface((100, 100))
            # Заливаем разными цветами для визуального различия
            color = (50 + i * 20, 100 - i * 10, 150 + i * 15)
            preview.fill(color)

            # Добавляем название файла
            font = pygame.font.Font(None, 16)
            text = font.render(os.path.splitext(map_file)[0], True, (255, 255, 255))
            text_rect = text.get_rect(center=(50, 15))
            preview.blit(text, text_rect)

            # Добавляем информацию о размере
            size_text = font.render("64x64", True, (200, 200, 200))  # Заглушка
            size_rect = size_text.get_rect(center=(50, 85))
            preview.blit(size_text, size_rect)

            self.map_thumbnails.append(preview)

    def scroll_maps(self, direction):
        """Прокручивает список карт"""
        max_offset = max(0, len(self.map_files) - self.items_per_page)
        self.scroll_offset = max(0, min(max_offset, self.scroll_offset + direction))

    def get_map_files(self):
        """Возвращает список доступных карт"""
        if not os.path.exists("maps"):
            return []

        return [f for f in os.listdir("maps") if f.endswith('.json')]

    def load_map(self, filepath):
        """Загружает карту из файла"""
        try:
            with open(filepath, 'r') as f:
                map_info = json.load(f)

            self.map = Map(map_info['size'], map_info['size'], map_info.get('default_tile', 'grass'))
            self.map.tiles = map_info['tiles']
            self.show_load_dialog = False
            print(f"Карта {os.path.basename(filepath)} загружена")
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")

    def toggle_grid(self):
        if self.map:
            self.map.show_grid = not self.map.show_grid
            self.grid_button.text = f"Сетка: {'ВКЛ' if self.map.show_grid else 'ВЫКЛ'}"
