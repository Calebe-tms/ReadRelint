import pytest
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

def test_get_monitoring_status():
    response = client.get("/api/v1/monitoring/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_monitoring" in data
    assert "use_llm" in data
    assert "total_files_in_folder" in data
    assert "read_files_in_folder" in data

def test_toggle_llm():
    response = client.post("/api/v1/monitoring/toggle-llm", json={"use_llm": False})
    assert response.status_code == 200
    data = response.json()
    assert data["use_llm"] is False

def test_set_invalid_monitoring_path():
    response = client.post("/api/v1/monitoring/path", json={"path": "C:/pasta_inexistente_12345"})
    assert response.status_code == 404

def test_stop_monitoring():
    response = client.post("/api/v1/monitoring/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
