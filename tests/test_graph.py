"""Модуль тестов для построения графа зависимостей"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.main import (
    build_dependency_graph,
    load_test_repo,
)


class TestLoadTestRepo(unittest.TestCase):
    """Тесты загрузки тестового репозитория"""

    def test_file_not_found(self) -> None:
        """Проверяет обработку отсутствующего файла"""
        with self.assertRaises(FileNotFoundError):
            load_test_repo("nonexistent.json")

    def test_invalid_json(self) -> None:
        """Проверяет обработку невалидного JSON"""
        with TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{bad}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_test_repo(str(bad))

    def test_valid_repo(self) -> None:
        """Проверяет загрузку корректного файла"""
        with TemporaryDirectory() as tmp:
            good = Path(tmp) / "repo.json"
            good.write_text(
                '{"A": ["B"], "B": []}',
                encoding="utf-8",
            )
            result = load_test_repo(str(good))
            self.assertEqual(result["A"], ["B"])


class TestBuildGraph(unittest.TestCase):
    """Тесты построения графа зависимостей"""

    def test_simple_graph(self) -> None:
        """Проверяет построение простого графа"""
        packages = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        graph = build_dependency_graph("A", packages)
        self.assertIn("A", graph)
        self.assertIn("B", graph)
        self.assertIn("C", graph)
        self.assertIn("D", graph)
        self.assertEqual(graph["A"], ["B", "C"])

    def test_cycle_handling(self) -> None:
        """Проверяет обработку циклических зависимостей"""
        packages = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        graph = build_dependency_graph("A", packages)
        self.assertEqual(len(graph), 3)
        self.assertIn("A", graph)
        self.assertIn("B", graph)
        self.assertIn("C", graph)

    def test_filter_substring(self) -> None:
        """Проверяет фильтрацию по подстроке"""
        packages = {
            "A": ["B", "C_test", "D"],
            "B": [],
            "C_test": ["F"],
            "D": [],
            "F": [],
        }
        graph = build_dependency_graph(
            "A", packages, "test"
        )
        self.assertNotIn("C_test", graph["A"])
        self.assertNotIn("C_test", graph)

    def test_unknown_package(self) -> None:
        """Проверяет обработку неизвестного пакета"""
        packages = {"A": ["B"], "B": []}
        graph = build_dependency_graph("Z", packages)
        self.assertEqual(graph, {"Z": []})

    def test_empty_dependencies(self) -> None:
        """Проверяет пакет без зависимостей"""
        packages = {"A": []}
        graph = build_dependency_graph("A", packages)
        self.assertEqual(graph["A"], [])


if __name__ == "__main__":
    unittest.main()