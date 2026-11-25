import ast
import re

import pytest

from app.security.headers import HEADERS_FILE

REPO_ROOT = HEADERS_FILE.parent
TESTS_DOC = REPO_ROOT / "docs" / "TESTS.md"
TESTS_DIR = REPO_ROOT / "backend" / "tests"
REFERENCE = re.compile(r"`(test_[a-z0-9_]+\.py)::(test_[a-z0-9_]+)`")
FRONTEND_FILE = re.compile(r"`(src/[A-Za-z0-9_./-]+\.test\.ts)`")


def references() -> list[tuple[str, str]]:
    return REFERENCE.findall(TESTS_DOC.read_text(encoding="utf-8"))


def defined_tests(filename: str) -> set[str]:
    tree = ast.parse((TESTS_DIR / filename).read_text(encoding="utf-8"))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}


def plan_rows() -> list[tuple[int, str]]:
    rows = re.findall(r"^\| (\d+) \|(.*)$", TESTS_DOC.read_text(encoding="utf-8"), re.MULTILINE)
    return [(int(number), rest) for number, rest in rows]


def test_the_plan_covers_all_nineteen_backend_items():
    assert [number for number, _ in plan_rows()] == list(range(1, 20))


def test_every_item_names_at_least_one_readable_test():
    assert [number for number, rest in plan_rows() if not REFERENCE.search(rest)] == []


@pytest.mark.parametrize(("filename", "name"), references(), ids=lambda value: value)
def test_every_listed_backend_test_exists(filename, name):
    assert name in defined_tests(filename)


def test_every_listed_frontend_test_file_exists():
    files = FRONTEND_FILE.findall(TESTS_DOC.read_text(encoding="utf-8"))

    assert files
    assert [path for path in files if not (REPO_ROOT / path).is_file()] == []
