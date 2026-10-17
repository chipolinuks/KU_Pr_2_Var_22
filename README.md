# KU_Pr_2_Var_22

## Общее описание

CLI-инструмент для визуализации графа зависимостей пакетов
менеджера **Alpine Linux (apk)**. Позволяет анализировать
прямые и транзитивные зависимости, строить граф и выводить
его в виде изображения (PNG) или ASCII-дерева.

Инструмент разрабатывается в рамках дисциплины
«Конфигурационное управление» (РТУ МИРЭА, ИКБО-21-25,
вариант 22).

На текущем этапе (этап 1) реализован **минимальный прототип
с конфигурацией**: чтение параметров из JSON-файла, их
валидация и вывод в формате ключ-значение.

## Описание настроек

Все параметры задаются в JSON-файле конфигурации
(по умолчанию `config.json`):

| Параметр           | Тип    | Описание                                   |
|--------------------|--------|--------------------------------------------|
| `package_name`     | string | Имя анализируемого пакета                  |
| `repo_url`         | string | URL репозитория или путь к тестовому файлу |
| `test_mode`        | bool   | Режим работы с тестовым репозиторием       |
| `output_image`     | string | Имя файла для изображения графа            |
| `ascii_tree`       | bool   | Вывод зависимостей в виде ASCII-дерева     |
| `filter_substring` | string | Подстрока для фильтрации пакетов           |

## Описание функций

- `load_config(path)` — загружает JSON-файл конфигурации
- `validate_config(config)` — валидирует все параметры
- `validate_package_name(value)` — проверяет имя пакета
- `validate_repo_url(value)` — проверяет URL/путь
- `validate_bool(value, name)` — проверяет булев параметр
- `validate_output_image(value)` — проверяет имя файла
- `validate_filter(value)` — проверяет подстроку фильтра
- `print_config(config)` — выводит параметры в консоль
- `main()` — точка входа в приложение

## Сборка и запуск тестов

Запуск приложения (универсальный способ):

```bash
python src/main.py                 # использует config.json
python src/main.py my_config.json  # использует указанный файл

## Примеры использования

Пример `config.json`:

```json
{
    "package_name": "curl",
    "repo_url": "https://pkgs.alpinelinux.org/packages",
    "test_mode": false,
    "output_image": "deps.png",
    "ascii_tree": false,
    "filter_substring": ""
}
```

Вывод приложения:

```
=== Конфигурация приложения ===
package_name = 'curl'
repo_url = 'https://pkgs.alpinelinux.org/packages'
test_mode = False
output_image = 'deps.png'
ascii_tree = False
filter_substring = ''
===============================
```