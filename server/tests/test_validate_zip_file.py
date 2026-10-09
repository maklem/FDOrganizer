import io
import zipfile

import pytest

from server import APP
from server.package import validate_zip_file


def build_zip(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for name, payload in entries:
            zip_file.writestr(name, payload)
    buffer.seek(0)
    return zipfile.ZipFile(buffer, "r")


@pytest.fixture
def zip_limits():
    original_content_length = APP.config.get("MAX_CONTENT_LENGTH")
    original_package_size = APP.config.get("MAX_PACKAGE_SIZE")
    APP.config["MAX_CONTENT_LENGTH"] = 1_000_000
    APP.config["MAX_PACKAGE_SIZE"] = 1_000_000
    yield
    APP.config["MAX_CONTENT_LENGTH"] = original_content_length
    APP.config["MAX_PACKAGE_SIZE"] = original_package_size


def test_validate_zip_file_accepts_valid_zip(zip_limits):
    with build_zip([
        ("first.txt", b"hello"),
        ("folder/second.txt", b"world"),
    ]) as zip_file:
        assert validate_zip_file(zip_file) is None


def test_validate_zip_file_rejects_absolute_paths(zip_limits):
    with build_zip([("/etc/passwd", b"nope")]) as zip_file:
        assert validate_zip_file(zip_file) == "Archive contains absolute path: /etc/passwd"


def test_validate_zip_file_rejects_path_traversal(zip_limits):
    with build_zip([("../evil.txt", b"nope")]) as zip_file:
        assert validate_zip_file(zip_file) == "Archive contains path traversal: ../evil.txt"


def test_validate_zip_file_rejects_too_many_files(zip_limits):
    entries = [(f"file-{index}.txt", b"abc") for index in range(1001)]
    with build_zip(entries) as zip_file:
        assert validate_zip_file(zip_file) == "Too many files in ZIP. (1001 > 1000)"


def test_validate_zip_file_rejects_entries_larger_than_max_content_length(zip_limits):
    APP.config["MAX_CONTENT_LENGTH"] = 10
    with build_zip([("large.txt", b"x" * 11)]) as zip_file:
        assert validate_zip_file(zip_file) == "Entry 'large.txt' too large (11 > 10)"


def test_validate_zip_file_rejects_long_entry_paths(zip_limits):
    long_name = "a" * 201 + ".txt"
    with build_zip([(long_name, b"x")]) as zip_file:
        assert validate_zip_file(zip_file) == f"Entry path too long: {long_name}"


def test_validate_zip_file_rejects_total_uncompressed_size_too_large(zip_limits):
    APP.config["MAX_PACKAGE_SIZE"] = 10
    with build_zip([("small-1.txt", b"x" * 6), ("small-2.txt", b"x" * 6)]) as zip_file:
        assert validate_zip_file(zip_file) == "Total uncompressed size too large (12 > 10)"
