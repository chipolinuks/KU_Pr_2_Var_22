"""Главный модуль CLI-приложения для анализа зависимостей apk"""

import json
import sys
from pathlib import Path


CONFIG_PATH_DEFAULT = "config.json"
URL_SCHEMES = ("http://", "https://")


def load_config(path: str) -> dict:
    """Загружает конфигурацию из JSON-файла"""
    config_file = Path(path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"Файл конфигурации не найден: {path}"
        )
    try:
        with config_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка разбора JSON: {e}") from e


def validate_package_name(value: object) -> str:
    """Проверяет имя анализируемого пакета"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "package_name должен быть непустой строкой"
        )
    return value.strip()


def validate_repo_url(value: object) -> str:
    """Проверяет URL репозитория или путь к файлу"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "repo_url должен быть непустой строкой"
        )
    value = value.strip()
    is_url = value.startswith(URL_SCHEMES)
    is_file = Path(value).exists()
    if not is_url and not is_file:
        raise ValueError(
            "repo_url должен быть URL или "
            "путём к существующему файлу"
        )
    return value


def validate_bool(value: object, name: str) -> bool:
    """Проверяет булев параметр конфигурации"""
    if not isinstance(value, bool):
        raise ValueError(f"{name} должен быть bool")
    return value


def validate_output_image(value: object) -> str:
    """Проверяет имя файла для изображения графа"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "output_image должен быть непустой строкой"
        )
    value = value.strip()
    if not Path(value).suffix:
        raise ValueError(
            "output_image должен иметь расширение"
        )
    return value


def validate_filter(value: object) -> str:
    """Проверяет подстроку для фильтрации пакетов"""
    if not isinstance(value, str):
        raise ValueError(
            "filter_substring должен быть строкой"
        )
    return value


REQUIRED_KEYS = (
    "package_name",
    "repo_url",
    "test_mode",
    "output_image",
    "ascii_tree",
    "filter_substring",
)


def validate_config(config: dict) -> dict:
    """Валидирует все параметры конфигурации"""
    if not isinstance(config, dict):
        raise ValueError(
            "Конфигурация должна быть объектом JSON"
        )
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Отсутствует параметр: {key}")
    return {
        "package_name": validate_package_name(
            config["package_name"]
        ),
        "repo_url": validate_repo_url(config["repo_url"]),
        "test_mode": validate_bool(
            config["test_mode"], "test_mode"
        ),
        "output_image": validate_output_image(
            config["output_image"]
        ),
        "ascii_tree": validate_bool(
            config["ascii_tree"], "ascii_tree"
        ),
        "filter_substring": validate_filter(
            config["filter_substring"]
        ),
    }


def print_config(config: dict) -> None:
    """Выводит параметры в формате ключ-значение"""
    print("=== Конфигурация приложения ===")
    for key, value in config.items():
        print(f"{key} = {value!r}")
    print("===============================")


def main() -> int:
    """Точка входа в приложение"""
    config_path = (
        sys.argv[1] if len(sys.argv) > 1
        else CONFIG_PATH_DEFAULT
    )
    try:
        raw_config = load_config(config_path)
        config = validate_config(raw_config)
        print_config(config)
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(
            f"Ошибка конфигурации: {e}", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())