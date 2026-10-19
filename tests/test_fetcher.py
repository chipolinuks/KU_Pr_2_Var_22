"""Модуль тестов для получения зависимостей"""

import unittest
from src.fetcher import _extract_dependencies


class TestExtractDependencies(unittest.TestCase):
    """Тесты функции извлечения зависимостей"""

    def test_found_with_deps(self) -> None:
        """Проверяет извлечение зависимостей при наличии"""
        content = "P:curl\nV:1.0\nD:libc libssl\n"
        deps = _extract_dependencies(content, "curl")
        self.assertEqual(deps, ["libc", "libssl"])

    def test_found_no_deps(self) -> None:
        """Проверяет пакет без зависимостей"""
        content = "P:empty-pkg\nV:1.0\n"
        deps = _extract_dependencies(content, "empty-pkg")
        self.assertEqual(deps, [])

    def test_not_found(self) -> None:
        """Проверяет отсутствие пакета в индексе"""
        content = "P:other-pkg\nV:1.0\nD:libc\n"
        deps = _extract_dependencies(content, "curl")
        self.assertEqual(deps, [])

    def test_multiple_blocks(self) -> None:
        """Проверяет корректный поиск среди нескольких блоков"""
        content = "P:pkg1\nD:dep1\n\nP:curl\nD:libc libssl\n\nP:pkg2"
        deps = _extract_dependencies(content, "curl")
        self.assertEqual(deps, ["libc", "libssl"])


if __name__ == "__main__":
    unittest.main()