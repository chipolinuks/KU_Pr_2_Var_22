"""Модуль тестов для валидации конфигурации"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.main import (
    load_config,
    validate_config,
    validate_package_name,
    validate_repo_url,
)


class TestLoadConfig(unittest.TestCase):
    """Тесты загрузки JSON-конфигурации"""

    def test_file_not_found(self) -> None:
        """Проверяет обработку отсутствующего файла"""
        with self.assertRaises(FileNotFoundError):
            load_config("nonexistent.json")

    def test_invalid_json(self) -> None:
        """Проверяет обработку невалидного JSON"""
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(
                "{not valid json", encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                load_config(str(bad))

    def test_valid_json(self) -> None:
        """Проверяет успешную загрузку корректного JSON"""
        with TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.json"
            good.write_text('{"a": 1}', encoding="utf-8")
            self.assertEqual(
                load_config(str(good)), {"a": 1}
            )


class TestValidators(unittest.TestCase):
    """Тесты отдельных валидаторов параметров"""

    def test_package_name_valid(self) -> None:
        """Проверяет валидное имя пакета"""
        self.assertEqual(
            validate_package_name("curl"), "curl"
        )

    def test_package_name_empty(self) -> None:
        """Проверяет реакцию на пустое имя пакета"""
        with self.assertRaises(ValueError):
            validate_package_name("")

    def test_package_name_not_string(self) -> None:
        """Проверяет реакцию на не-строку"""
        with self.assertRaises(ValueError):
            validate_package_name(123)

    def test_repo_url_http(self) -> None:
        """Проверяет валидный HTTP URL"""
        self.assertEqual(
            validate_repo_url("https://example.com"),
            "https://example.com",
        )

    def test_repo_url_invalid(self) -> None:
        """Проверяет реакцию на некорректный URL"""
        with self.assertRaises(ValueError):
            validate_repo_url("not-a-url-and-not-a-file")


class TestValidateConfig(unittest.TestCase):
    """Тесты комплексной валидации конфигурации"""

    def _make_valid(self, tmp: Path) -> str:
        """Создаёт валидный JSON-файл и возвращает путь"""
        path = tmp / "cfg.json"
        data = {
            "package_name": "curl",
            "repo_url": "https://example.com",
            "test_mode": False,
            "output_image": "deps.png",
            "ascii_tree": True,
            "filter_substring": "",
        }
        path.write_text(
            json.dumps(data), encoding="utf-8"
        )
        return str(path)

    def test_missing_key(self) -> None:
        """Проверяет реакцию на отсутствующий ключ"""
        with self.assertRaises(ValueError):
            validate_config({"package_name": "curl"})

    def test_full_valid_config(self) -> None:
        """Проверяет полную валидацию корректной конфигурации"""
        with TemporaryDirectory() as tmp:
            path = self._make_valid(Path(tmp))
            raw = load_config(path)
            result = validate_config(raw)
            self.assertEqual(result["package_name"], "curl")
            self.assertTrue(result["ascii_tree"])


if __name__ == "__main__":
    unittest.main()