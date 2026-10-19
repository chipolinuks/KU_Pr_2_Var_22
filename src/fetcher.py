"""Модуль для получения данных о зависимостях пакетов apk"""

import gzip
import tarfile
import urllib.error
import urllib.request
from io import BytesIO


def download_apkindex(url: str) -> bytes:
    """Скачивает файл APKINDEX.tar.gz по указанному URL"""
    req = urllib.request.Request(url, headers={"User-Agent": "Python"})
    with urllib.request.urlopen(req) as response:
        return response.read()


def parse_apkindex(data: bytes, package_name: str) -> list[str]:
    """Извлекает прямые зависимости указанного пакета из данных APKINDEX"""
    with gzip.GzipFile(fileobj=BytesIO(data)) as gz:
        with tarfile.open(fileobj=gz, mode="r:") as tar:
            member = tar.getmember("APKINDEX")
            f = tar.extractfile(member)
            if f is None:
                raise ValueError("Не удалось извлечь файл APKINDEX")
            content = f.read().decode("utf-8")
    return _extract_dependencies(content, package_name)


def _extract_dependencies(content: str, package_name: str) -> list[str]:
    """Ищет блок пакета и возвращает список его зависимостей"""
    blocks = content.split("\n\n")
    for block in blocks:
        lines = block.split("\n")
        pkg_name = ""
        deps = ""
        for line in lines:
            if line.startswith("P:"):
                pkg_name = line[2:].strip()
            elif line.startswith("D:"):
                deps = line[2:].strip()
        if pkg_name == package_name:
            if deps:
                return [dep.strip() for dep in deps.split() if dep.strip()]
            return []
    return []