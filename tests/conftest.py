import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-KEY": settings.api_key}


def create_mock_doc(doc_id, data):
    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.to_dict.return_value = data
    return mock_doc


@pytest.fixture
def mock_db():
    with patch("app.routers.health.get_db") as mock_get_db:
        mock_firestore = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "test-doc-id"
        
        mock_collection = MagicMock()
        mock_firestore.collection.return_value.document.return_value.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        mock_get_db.return_value = mock_firestore
        yield mock_firestore


@pytest.fixture
def mock_db_with_data():
    with patch("app.routers.health.get_db") as mock_get_db:
        mock_firestore = MagicMock()
        
        mock_docs = [
            create_mock_doc("doc1", {
                "timestamp": datetime(2026, 1, 8, 8, 30),
                "steps": 1200,
                "calories": 450,
                "sleepHours": 7.5
            }),
            create_mock_doc("doc2", {
                "timestamp": datetime(2026, 1, 9, 9, 0),
                "steps": 1500,
                "calories": 500,
                "sleepHours": 8.0
            })
        ]
        
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = mock_docs
        
        mock_collection = MagicMock()
        mock_collection.where.return_value = mock_query
        
        mock_firestore.collection.return_value.document.return_value.collection.return_value = mock_collection
        
        mock_get_db.return_value = mock_firestore
        yield mock_firestore


@pytest.fixture
def mock_db_empty():
    with patch("app.routers.health.get_db") as mock_get_db:
        mock_firestore = MagicMock()
        
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_collection = MagicMock()
        mock_collection.where.return_value = mock_query
        
        mock_firestore.collection.return_value.document.return_value.collection.return_value = mock_collection
        
        mock_get_db.return_value = mock_firestore
        yield mock_firestore
