import json
import os


def load_settings():
    """Загрузка настроек из файла или создание дефолтных"""
    default_settings = {
        "resolution": [1280, 720],
        "fullscreen": False,
        "music_volume": 0.8,
        "sfx_volume": 1.0
    }

    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)

                # Обработка разрешения
                if isinstance(settings["resolution"], list):
                    # Убедимся, что значения - числа
                    settings["resolution"] = [
                        int(settings["resolution"][0]),
                        int(settings["resolution"][1])
                    ]
                elif isinstance(settings["resolution"], str):
                    # Конвертируем строку "1280x720" в список [1280, 720]
                    w, h = settings["resolution"].split('x')
                    settings["resolution"] = [int(w), int(h)]

                return settings
    except Exception as e:
        print(f"Ошибка загрузки настроек: {e}")
        print("Используются настройки по умолчанию")

    return default_settings


def save_settings(settings):
    """Сохранение настроек в файл"""
    try:
        with open("settings.json", "w") as f:
            # Сохраняем копию настроек, чтобы не менять оригинал
            settings_copy = settings.copy()
            json.dump(settings_copy, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")
