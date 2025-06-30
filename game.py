import pygame
from scenes.main_menu import MainMenuScene
from scenes.map_select import MapSelectScene
from scenes.settings import SettingsScene
from scenes.game import GameScene
from scenes.map_editor import MapEditorScene
from scenes.map_editor_menu import MapEditorMenuScene
from scenes.map_editor_params import MapEditorParamsScene
from utils.settings import load_settings, save_settings


class Game:
    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = True
        self.scenes = {}
        self.current_scene = None
        self.current_scene_name = None
        self.settings = load_settings()
        self.editor_params = None
        self.init_screen()
        self.init_scenes()

    def init_scenes(self):
        """Создаем или пересоздаем все сцены"""
        self.scenes = {
            "main_menu": MainMenuScene(self),
            "map_select": MapSelectScene(self),
            "settings": SettingsScene(self),
            "game": GameScene(self),
            "map_editor": MapEditorScene(self),
            "map_editor_menu": MapEditorMenuScene(self),
            "map_editor_params": MapEditorParamsScene(self),
        }

    def load_settings(self):
        return load_settings()

    def save_settings(self):
        save_settings(self.settings)

    def init_screen(self):
        width, height = self.settings["resolution"]
        flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("Selectown")

    def run(self):
        self.change_scene("main_menu")

        while self.running:
            dt = self.clock.tick(60) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update(dt)
                self.current_scene.render(self.screen)

            pygame.display.flip()

    def change_scene(self, scene_name):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = self.scenes[scene_name]
        self.current_scene_name = scene_name
        self.current_scene.on_enter()

    def quit(self):
        self.running = False

    def reload_scenes(self):
        """Пересоздает все сцены с новыми настройками"""
        # Сохраняем имя текущей сцены
        current_scene_name = self.current_scene_name

        # Пересоздаем сцены
        self.init_scenes()

        # Восстанавливаем текущую сцену по имени
        self.change_scene(current_scene_name)