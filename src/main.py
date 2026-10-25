"""Главный модуль CLI-приложения для анализа зависимостей apk"""

import json
import sys
import urllib.error
from pathlib import Path

from src.fetcher import download_apkindex

CONFIG_PATH_DEFAULT = "configs/config_simple.json"


def load_config(path: str) -> dict:
    """Загружает конфигурацию из JSON-ls-файла"""
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
    is_url = value.startswith(("http://", "https://"))
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


def parse_all_packages(data: str) -> dict:
    """Парсит весь APKINDEX в словарь всех пакетов и их зависимостей"""
    packages = {}
    current_pkg = None
    for line in data.splitlines():
        if line.startswith("P:"):
            current_pkg = line[2:].strip()
            packages[current_pkg] = []
        elif line.startswith("D:") and current_pkg:
            deps_str = line[2:].strip()
            deps = []
            for dep in deps_str.split():
                name = dep.split("=")[0]
                if name.startswith("so:"):
                    name = name[3:]
                deps.append(name)
            packages[current_pkg] = deps
    return packages


def load_test_repo(path: str) -> dict:
    """Загружает тестовый репозиторий из JSON-файла"""
    repo_file = Path(path)
    if not repo_file.exists():
        raise FileNotFoundError(
            f"Тестовый файл не найден: {path}"
        )
    try:
        with repo_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка разбора JSON: {e}") from e


def build_dependency_graph(
    package_name: str,
    packages: dict,
    filter_sub: str = "",
) -> dict:
    """Строит граф зависимостей с помощью DFS с рекурсией"""
    graph = {}
    visited = set()

    def dfs(pkg: str) -> None:
        """Рекурсивный обход в глубину"""
        if pkg in visited:
            return
        visited.add(pkg)

        deps = packages.get(pkg, [])
        filtered_deps = []
        for dep in deps:
            if filter_sub and filter_sub in dep:
                continue
            filtered_deps.append(dep)

        graph[pkg] = filtered_deps

        for dep in filtered_deps:
            if dep not in visited and dep in packages:
                dfs(dep)

    dfs(package_name)
    return graph


def print_graph(graph: dict) -> None:
    """Выводит граф зависимостей на экран"""
    print("\n=== Граф зависимостей ===")
    for pkg, deps in graph.items():
        if deps:
            deps_str = ", ".join(deps)
            print(f"{pkg} -> {deps_str}")
        else:
            print(f"{pkg} -> (нет зависимостей)")
    print("=========================")


def run_stage3(config: dict) -> None:
    """Выполняет построение графа зависимостей (Этап 3)"""
    print("\n=== Построение графа зависимостей ===")
    repo_url = config["repo_url"]
    package_name = config["package_name"]
    filter_sub = config["filter_substring"]
    test_mode = config["test_mode"]

    if test_mode:
        packages = load_test_repo(repo_url)
    else:
        data = download_apkindex(repo_url)
        packages = parse_all_packages(data)

    graph = build_dependency_graph(
        package_name, packages, filter_sub
    )
    print_graph(graph)


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
        run_stage3(config)
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        return 1
    except urllib.error.URLError:
        return 1


if __name__ == "__main__":
    sys.exit(main())