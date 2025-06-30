import pygame


class Dropdown:
    def __init__(self, x, y, width, height, options, default_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        self.option_rects = []
        self.last_click_time = 0
        self.z_index = 0
        self.surface = None  # Поверхность для открытого списка

        # Цвета
        self.bg_color = (70, 70, 90)
        self.hover_color = (100, 100, 120)
        self.selected_color = (120, 120, 150)
        self.text_color = (255, 255, 255)
        self.border_color = (50, 50, 70)
        self.shadow_color = (0, 0, 0, 100)

        # Шрифт
        self.font = pygame.font.Font(None, 28)

        # Создаем прямоугольники для опций
        for i in range(len(options)):
            self.option_rects.append(pygame.Rect(x, y + height * (i + 1), width, height))

    def get_selected(self):
        return self.options[self.selected_index]

    def set_z_index(self, z_index):
        self.z_index = z_index

    def handle_event(self, event):
        # Проверяем, что событие не None
        if event is None:
            return False

        current_time = pygame.time.get_ticks()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем, было ли нажатие на основной прямоугольник
            if self.rect.collidepoint(event.pos):
                if current_time - self.last_click_time > 300:
                    self.is_open = not self.is_open
                    self.last_click_time = current_time
                    # При открытии создаем новую поверхность
                    if self.is_open:
                        self.create_open_list_surface()
                return True

            # Если выпадающий список открыт, проверяем опции
            if self.is_open and self.surface:
                # Переводим координаты мыши в координаты поверхности списка
                rel_pos = (event.pos[0], event.pos[1])

                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(rel_pos):
                        if current_time - self.last_click_time > 300:
                            self.selected_index = i
                            self.is_open = False
                            self.last_click_time = current_time
                        return True

            # Если нажали вне выпадающего списка, закрываем его
            if self.is_open:
                self.is_open = False
                return True

        return False

    def create_open_list_surface(self):
        """Создает поверхность для открытого списка с правильными размерами"""
        # Определяем размеры для поверхности
        height = self.rect.height * (len(self.options) + 1)
        width = self.rect.width

        # Создаем поверхность с альфа-каналом
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Рисуем фон для всего списка
        pygame.draw.rect(self.surface, self.shadow_color, (0, 0, width, height), border_radius=4)

        # Рисуем основной прямоугольник (верхний элемент)
        pygame.draw.rect(self.surface, self.bg_color, (0, 0, width, self.rect.height), border_radius=4)
        pygame.draw.rect(self.surface, self.border_color, (0, 0, width, self.rect.height), 2, border_radius=4)

        # Текст выбранной опции
        text = self.font.render(self.options[self.selected_index], True, self.text_color)
        text_rect = text.get_rect(midleft=(10, self.rect.height // 2))
        self.surface.blit(text, text_rect)

        # Стрелка вниз
        arrow_size = 6
        arrow_x = width - 20
        arrow_y = self.rect.height // 2
        pygame.draw.polygon(self.surface, self.text_color, [
            (arrow_x, arrow_y - arrow_size // 2),
            (arrow_x + arrow_size, arrow_y - arrow_size // 2),
            (arrow_x + arrow_size // 2, arrow_y + arrow_size // 2)
        ])

        # Рисуем опции
        for i, rect in enumerate(self.option_rects):
            y_pos = self.rect.height * (i + 1)

            # Выделяем выбранный элемент другим цветом
            if i == self.selected_index:
                item_color = self.selected_color
            else:
                # Для определения наведения нужно будет обрабатывать в реальном времени
                item_color = self.bg_color

            pygame.draw.rect(self.surface, item_color, (0, y_pos, width, self.rect.height), border_radius=4)
            pygame.draw.rect(self.surface, self.border_color, (0, y_pos, width, self.rect.height), 2, border_radius=4)

            option_text = self.font.render(self.options[i], True, self.text_color)
            option_rect = option_text.get_rect(midleft=(10, y_pos + self.rect.height // 2))
            self.surface.blit(option_text, option_rect)

    def draw_closed(self, surface):
        """Рисует закрытое состояние выпадающего списка"""
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=4)

        text = self.font.render(self.options[self.selected_index], True, self.text_color)
        text_rect = text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text, text_rect)

        arrow_size = 6
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        pygame.draw.polygon(surface, self.text_color, [
            (arrow_x, arrow_y - arrow_size // 2),
            (arrow_x + arrow_size, arrow_y - arrow_size // 2),
            (arrow_x + arrow_size // 2, arrow_y + arrow_size // 2)
        ])

    def draw_open(self, surface):
        """Рисует открытое состояние выпадающего списка"""
        if not self.is_open or not self.surface:
            return

        # Обновляем подсветку при наведении в реальном времени
        mouse_pos = pygame.mouse.get_pos()
        rel_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)

        # Создаем временную поверхность для обновления
        updated_surface = self.surface.copy()

        # Обновляем подсветку для опций
        for i, rect in enumerate(self.option_rects):
            y_pos = self.rect.height * (i + 1)

            # Пропускаем выбранный элемент
            if i == self.selected_index:
                continue

            # Определяем цвет в зависимости от наведения
            if rect.collidepoint(rel_pos):
                item_color = self.hover_color
            else:
                item_color = self.bg_color

            pygame.draw.rect(updated_surface, item_color, (0, y_pos, self.rect.width, self.rect.height),
                             border_radius=4)
            pygame.draw.rect(updated_surface, self.border_color, (0, y_pos, self.rect.width, self.rect.height), 2,
                             border_radius=4)

            option_text = self.font.render(self.options[i], True, self.text_color)
            option_rect = option_text.get_rect(midleft=(10, y_pos + self.rect.height // 2))
            updated_surface.blit(option_text, option_rect)

        # Рисуем всю поверхность списка поверх основного экрана
        surface.blit(updated_surface, (self.rect.x, self.rect.y))
