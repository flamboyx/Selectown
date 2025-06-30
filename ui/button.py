import pygame


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.colors = {
            "normal": (70, 130, 180),
            "hover": (100, 160, 210),
            "pressed": (50, 100, 150)
        }
        self.state = "normal"
        self.font = pygame.font.Font(None, 36)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.state = "pressed"
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.rect.collidepoint(event.pos) and self.state == "pressed":
                self.state = "hover"
                if self.action:
                    self.action()

    def handle_hover(self, pos):
        if self.rect.collidepoint(pos):
            if self.state != "pressed":
                self.state = "hover"
        else:
            self.state = "normal"

    def draw(self, surface):
        pygame.draw.rect(surface, self.colors[self.state], self.rect, border_radius=8)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
