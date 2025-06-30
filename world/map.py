import pygame


class Map:
    def __init__(self, width, height, default_tile='grass'):
        self.width = width
        self.height = height
        self.default_tile = default_tile
        self.tiles = [[default_tile for _ in range(width)] for _ in range(height)]
        self.tile_size = 24
        self.camera_x = 0
        self.camera_y = 0
        self.brush_size = 1
        self.show_grid = True

        self.grid_colors = [
            (30, 30, 30, 100),  # Исходный цвет
            (255, 255, 0, 150),  # Ярко-желтый
            (0, 255, 0, 150),  # Ярко-зеленый
            (255, 0, 0, 150),  # Ярко-красный
            (255, 255, 255, 200)  # Белый
        ]
        self.grid_color_index = 0
        self.grid_color = self.grid_colors[self.grid_color_index]

        self.grid_styles = ['lines', 'dots', 'dashed']
        self.grid_style_index = 0

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def set_tile(self, x, y, tile_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type

    def set_tiles_area(self, center_x, center_y, radius, tile_type):
        """Устанавливает тайлы в пределах круга с заданным радиусом"""
        radius_squared = radius * radius

        # Определяем границы области для проверки
        min_x = max(0, center_x - radius)
        max_x = min(self.width - 1, center_x + radius)
        min_y = max(0, center_y - radius)
        max_y = min(self.height - 1, center_y + radius)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                # Проверяем, попадает ли тайл в круг
                dx = x - center_x
                dy = y - center_y
                distance_squared = dx * dx + dy * dy

                if distance_squared <= radius_squared:
                    self.set_tile(x, y, tile_type)

    def fill_area(self, x, y, target_tile, replacement_tile):
        """Заливка области (рекурсивная)"""
        if target_tile == replacement_tile:
            return

        stack = [(x, y)]
        visited = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue

            if self.get_tile(cx, cy) != target_tile:
                continue

            self.set_tile(cx, cy, replacement_tile)

            # Добавляем соседей
            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))

    def toggle_grid_color(self):
        """Переключение цвета сетки по Shift+G"""
        self.grid_color_index = (self.grid_color_index + 1) % len(self.grid_colors)
        self.grid_color = self.grid_colors[self.grid_color_index]

    def toggle_grid_style(self):
        """Переключение стиля сетки по Ctrl+G"""
        self.grid_style_index = (self.grid_style_index + 1) % len(self.grid_styles)

    def draw_grid(self, surface, camera_offset_x, camera_offset_y):
        """Модифицированная отрисовка сетки с разными стилями"""
        if not self.show_grid:
            return

        grid_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        current_style = self.grid_styles[self.grid_style_index]

        if current_style == 'lines':
            # Оригинальный код рисования линий
            for x in range(self.width + 1):
                screen_x = x * self.tile_size - camera_offset_x
                pygame.draw.line(grid_surface, self.grid_color,
                                 (screen_x, 0), (screen_x, surface.get_height()), 1)
            for y in range(self.height + 1):
                screen_y = y * self.tile_size - camera_offset_y
                pygame.draw.line(grid_surface, self.grid_color,
                                 (0, screen_y), (surface.get_width(), screen_y), 1)

        elif current_style == 'dots':
            # Рисуем точки на пересечениях
            dot_radius = 1
            for x in range(self.width + 1):
                for y in range(self.height + 1):
                    screen_x = x * self.tile_size - camera_offset_x
                    screen_y = y * self.tile_size - camera_offset_y
                    pygame.draw.circle(grid_surface, self.grid_color,
                                       (screen_x, screen_y), dot_radius)

        elif current_style == 'dashed':
            # Пунктирные линии
            dash_length = 4
            gap_length = 4

            # Вертикальные линии
            for x in range(self.width + 1):
                screen_x = x * self.tile_size - camera_offset_x
                for y_start in range(0, surface.get_height(), dash_length + gap_length):
                    pygame.draw.line(grid_surface, self.grid_color,
                                     (screen_x, y_start),
                                     (screen_x, min(y_start + dash_length, surface.get_height())),
                                     1)

            # Горизонтальные линии
            for y in range(self.height + 1):
                screen_y = y * self.tile_size - camera_offset_y
                for x_start in range(0, surface.get_width(), dash_length + gap_length):
                    pygame.draw.line(grid_surface, self.grid_color,
                                     (x_start, screen_y),
                                     (min(x_start + dash_length, surface.get_width()), screen_y),
                                     1)

        surface.blit(grid_surface, (0, 0))

    def zoom_in(self):
        """Увеличивает масштаб"""
        if self.tile_size < 48:  # Максимальный размер
            self.tile_size += 4

    def zoom_out(self):
        """Уменьшает масштаб"""
        if self.tile_size > 8:  # Минимальный размер
            self.tile_size -= 4