from server.util import is_valid_filename


class TestFilenameValidation:
    def test_valid_simple_filename(self):
        assert is_valid_filename("document.pdf") is True
        assert is_valid_filename("file.txt") is True
        assert is_valid_filename("README") is True

    def test_valid_with_spaces(self):
        assert is_valid_filename("my file.txt") is True
        assert is_valid_filename("file name with spaces.doc") is True

    def test_valid_with_hyphens_underscores_dots(self):
        assert is_valid_filename("file-name.txt") is True
        assert is_valid_filename("file_name.txt") is True
        assert is_valid_filename("file.name.txt") is True
        assert is_valid_filename("file-name_123.txt") is True
        assert is_valid_filename("my-file_v1.0.txt") is True

    def test_valid_alphanumeric(self):
        assert is_valid_filename("abc123") is True
        assert is_valid_filename("123") is True
        assert is_valid_filename("ABC") is True

    def test_invalid_none(self):
        assert is_valid_filename(None) is False

    def test_invalid_empty(self):
        assert is_valid_filename("") is False

    def test_invalid_dot(self):
        assert is_valid_filename(".") is False

    def test_invalid_dot_dot(self):
        assert is_valid_filename("..") is False

    def test_invalid_path_separators(self):
        assert is_valid_filename("file/name.txt") is False
        assert is_valid_filename("file\\name.txt") is False
        assert is_valid_filename("folder/file.txt") is False
        assert is_valid_filename("folder\\file.txt") is False

    def test_invalid_with_path_traversal(self):
        assert is_valid_filename("../file.txt") is False
        assert is_valid_filename("../../etc/passwd") is False
        assert is_valid_filename("..\\file.txt") is False

    def test_invalid_control_characters(self):
        assert is_valid_filename("file\x00.txt") is False
        assert is_valid_filename("file\n.txt") is False
        assert is_valid_filename("file\r.txt") is False
        assert is_valid_filename("file\t.txt") is False
        assert is_valid_filename("file\x01.txt") is False

    def test_invalid_shellparameter(self):
        assert is_valid_filename("-") is False
        assert is_valid_filename("--") is False
        assert is_valid_filename("-v") is False
        assert is_valid_filename("--param") is False
        assert is_valid_filename("--param=value") is False

    def test_invalid_special_characters(self):
        assert is_valid_filename("file#name.txt") is False
        assert is_valid_filename("file$name.txt") is False
        assert is_valid_filename("file%name.txt") is False
        assert is_valid_filename("file&name.txt") is False
        assert is_valid_filename("file*name.txt") is False
        assert is_valid_filename("file{name}.txt") is False
        assert is_valid_filename("file|name.txt") is False
        assert is_valid_filename("file;name.txt") is False
        assert is_valid_filename("file:name.txt") is False
        assert is_valid_filename("file\"name.txt") is False
        assert is_valid_filename("file<name>.txt") is False
        assert is_valid_filename("file>name.txt") is False
        assert is_valid_filename("file?name.txt") is False
        assert is_valid_filename("file!name.txt") is False

    def test_invalid_with_leading_trailing_dots_in_path_context(self):
        assert is_valid_filename("./file.txt") is False
        assert is_valid_filename("folder/./file.txt") is False

    def test_edge_cases(self):
        assert is_valid_filename("a") is True
        assert is_valid_filename("a.b") is True
        assert is_valid_filename("a_b-c 123.txt") is True
        assert is_valid_filename("file.") is True
        assert is_valid_filename(".hidden") is True
        assert is_valid_filename("file..txt") is True
