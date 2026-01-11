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
