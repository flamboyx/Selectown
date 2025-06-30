import pygame


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.label = label

        # Цвета
        self.bg_color = (100, 100, 100)
        self.slider_color = (200, 200, 200)
        self.active_color = (50, 150, 255)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        # Рассчитываем значение на основе позиции мыши
        relative_x = mouse_x - self.rect.x
        percent = max(0, min(1, relative_x / self.rect.width))
        self.value = int(self.min_val + percent * (self.max_val - self.min_val))

    def get_value(self):
        return self.value

    def draw(self, surface):
        # Фон слайдера
        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Текущее положение
        percent = (self.value - self.min_val) / (self.max_val - self.min_val)
        slider_width = 20
        slider_x = self.rect.x + percent * self.rect.width - slider_width / 2
        slider_rect = pygame.Rect(slider_x, self.rect.y - 5, slider_width, self.rect.height + 10)

        # Рисуем ползунок
        color = self.active_color if self.dragging else self.slider_color
        pygame.draw.rect(surface, color, slider_rect, border_radius=3)

        # Текст с значением
        font = pygame.font.Font(None, 24)
        value_text = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        surface.blit(value_text, (self.rect.x, self.rect.y - 25))