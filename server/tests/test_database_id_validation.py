import pytest

from server import APP
from server.entities.errors import InvalidDocumentIdError
from server.router import validate_database_ids
from server.services.database import (
    assert_valid_document_id,
    is_valid_database_id,
)


class TestIsValidDatabaseId:
    def test_valid_couchdb_uuid(self):
        assert is_valid_database_id("3f9d1a2b4c5d6e7f8a9b0c1d2e3f4a5b") is True

    def test_valid_short_id(self):
        assert is_valid_database_id("abc123") is True

    def test_valid_uppercase_id(self):
        assert is_valid_database_id("ABC123XYZ") is True

    def test_valid_maximal_length(self):
        assert is_valid_database_id("a" * 64) is True

    def test_invalid_none(self):
        assert is_valid_database_id(None) is False

    def test_invalid_empty(self):
        assert is_valid_database_id("") is False

    def test_invalid_too_long(self):
        assert is_valid_database_id("a" * 65) is False

    def test_invalid_dot_dot(self):
        assert is_valid_database_id("..") is False

    def test_invalid_path_traversal(self):
        assert is_valid_database_id("../../etc/passwd") is False

    def test_invalid_slash(self):
        assert is_valid_database_id("abc/def") is False

    def test_invalid_backslash(self):
        assert is_valid_database_id("abc\\def") is False

    def test_invalid_query_characters(self):
        assert is_valid_database_id("abc?query=1") is False

    def test_invalid_fragment_character(self):
        assert is_valid_database_id("abc#fragment") is False

    def test_invalid_whitespace(self):
        assert is_valid_database_id("abc def") is False

    def test_invalid_unicode(self):
        assert is_valid_database_id("café") is False

    def test_invalid_control_characters(self):
        assert is_valid_database_id("abc\x00def") is False


class TestAssertValidDocumentId:
    def test_valid_id_does_not_raise(self):
        assert_valid_document_id("3f9d1a2b4c5d6e7f8a9b0c1d2e3f4a5b")

    def test_invalid_id_raises(self):
        with pytest.raises(InvalidDocumentIdError):
            assert_valid_document_id("../plugins/pwn")

    def test_error_contains_document_id(self):
        with pytest.raises(InvalidDocumentIdError) as error:
            assert_valid_document_id("not/a/valid/id")
        assert error.value.document_id == "not/a/valid/id"


class TestValidateDatabaseIdsHook:
    def test_valid_id_passes(self):
        with APP.test_request_context("/package/abc123/content"):
            assert validate_database_ids() is None

    def test_invalid_id_is_rejected(self):
        with APP.test_request_context("/package/not.a.valid.id/content"):
            response = validate_database_ids()
            assert response is not None
            assert response.status_code == 400

    def test_too_long_id_is_rejected(self):
        with APP.test_request_context(f"/package/{'a' * 65}/content"):
            response = validate_database_ids()
            assert response is not None
            assert response.status_code == 400

    def test_plain_id_parameter_is_rejected_when_invalid(self):
        with APP.test_request_context("/package/invalid..id/limits"):
            response = validate_database_ids()
            assert response is not None
            assert response.status_code == 400

    def test_non_id_route_arguments_are_skipped(self):
        # source and collection are no database ids; collection ids of
        # source plugins may legitimately contain other characters.
        with APP.test_request_context("/import/dummy/0_toplevel"):
            assert validate_database_ids() is None


class TestRoutesWithInvalidIds:
    def test_invalid_id_returns_400(self):
        client = APP.test_client()
        response = client.get("/login-oidc/not.a.valid.id")
        assert response.status_code == 400
        assert response.headers["Content-Type"].startswith("application/json")

    def test_invalid_id_is_rejected_before_database_access(self):
        client = APP.test_client()
        response = client.get("/login-keycloak/abc%3Fx=1")
        assert response.status_code == 400
        assert response.headers["Content-Type"].startswith("application/json")
