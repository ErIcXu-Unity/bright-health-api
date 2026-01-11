def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_health_data_valid(client, mock_db):
    payload = {
        "timestamp": "2026-01-08T08:30:00Z",
        "steps": 1200,
        "calories": 450,
        "sleepHours": 7.5
    }
    response = client.post("/users/user123/health-data", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "user123"
    assert data["steps"] == 1200
    assert data["calories"] == 450
    assert data["sleepHours"] == 7.5
    assert "id" in data


def test_create_health_data_negative_steps(client, mock_db):
    payload = {
        "timestamp": "2026-01-08T08:30:00Z",
        "steps": -100,
        "calories": 450,
        "sleepHours": 7.5
    }
    response = client.post("/users/user123/health-data", json=payload)
    assert response.status_code == 422


def test_create_health_data_missing_fields(client, mock_db):
    payload = {
        "timestamp": "2026-01-08T08:30:00Z",
        "steps": 1200
    }
    response = client.post("/users/user123/health-data", json=payload)
    assert response.status_code == 422


def test_get_health_data_valid(client, mock_db_with_data):
    response = client.get("/users/user123/health-data?start=01-01-2026&end=31-01-2026")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2
    assert data["page"] == 1
    assert data["total_count"] == 2
    assert data["has_more"] is False


def test_get_health_data_invalid_date_format(client, mock_db_with_data):
    response = client.get("/users/user123/health-data?start=2026-01-01&end=2026-01-31")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


def test_get_health_data_empty(client, mock_db_empty):
    response = client.get("/users/user123/health-data?start=01-01-2026&end=31-01-2026")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total_count"] == 0
    assert data["has_more"] is False


def test_get_health_data_pagination(client, mock_db_with_data):
    response = client.get("/users/user123/health-data?start=01-01-2026&end=31-01-2026&page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
