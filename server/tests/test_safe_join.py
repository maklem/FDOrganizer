from pathlib import Path

import pytest

from server.entities.errors import PathError
from server.util import safe_join


def test_safe_join_returns_joined_path(tmp_path):
    result = safe_join(tmp_path, "documents", "file.txt")

    assert isinstance(result, Path)
    assert result == tmp_path / "documents" / "file.txt"


def test_safe_join_accepts_string_base(tmp_path):
    result = safe_join(str(tmp_path), "file.txt")

    assert result == tmp_path / "file.txt"


def test_safe_join_without_segments_returns_base(tmp_path):
    assert safe_join(tmp_path) == tmp_path


@pytest.mark.parametrize(
    "segment",
    [
        "document.pdf",
        "my file.txt",
        "file-name_123.txt",
        "file[1].txt",
        "user@example.com",
        "a+b=c.txt",
        "file..txt",
        ".hidden",
        "file.",
    ],
)
def test_safe_join_accepts_valid_filenames(tmp_path, segment):
    assert safe_join(tmp_path, segment) == tmp_path / segment


@pytest.mark.parametrize(
    "segment",
    [
        "",
        ".",
        "..",
        "../escape.txt",
        "../../etc/passwd",
        "/etc/passwd",
        "folder/file.txt",
        "folder\\file.txt",
        "-rf",
        "--option",
        "file\x00.txt",
        "file\n.txt",
        "file\r.txt",
        "file\t.txt",
        "file#name.txt",
        "file:name.txt",
    ],
)
def test_safe_join_rejects_invalid_segments(tmp_path, segment):
    with pytest.raises(PathError):
        safe_join(tmp_path, segment)


def test_safe_join_validates_every_segment(tmp_path):
    with pytest.raises(PathError):
        safe_join(tmp_path, "valid", "..")


def test_safe_join_rejects_symlink_to_outside_directory(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    link = tmp_path / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are not supported")

    with pytest.raises(PathError):
        safe_join(tmp_path, "link", "file.txt")


def test_safe_join_rejects_symlink_to_outside_file(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    target = outside / "target.txt"
    target.write_text("secret", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks are not supported")

    with pytest.raises(PathError):
        safe_join(tmp_path, "link.txt")


def test_safe_join_allows_symlink_inside_base(tmp_path):
    inside = tmp_path / "inside"
    inside.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(inside, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are not supported")

    assert safe_join(tmp_path, "link", "file.txt") == link / "file.txt"
