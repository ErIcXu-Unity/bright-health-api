import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    with patch("app.routers.health.get_db") as mock_get_db:
        mock_firestore = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "test-doc-id"
        mock_firestore.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc_ref
        mock_get_db.return_value = mock_firestore
        yield mock_firestore
