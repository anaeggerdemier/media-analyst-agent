from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_run_agent():
    with patch("app.api.routes.run_agent") as mock:
        mock.return_value = {
            "response": "Search is the best performing channel with 5,000 users.",
            "tool_used": "get_channel_comparison",
        }
        yield mock


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_200(mock_run_agent):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Which channel has the best performance?"},
    )
    assert response.status_code == 200


def test_chat_response_structure(mock_run_agent):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Which channel has the best performance?"},
    )
    data = response.json()
    assert "response" in data
    assert "tool_used" in data


def test_chat_returns_tool_used(mock_run_agent):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Which channel has the best performance?"},
    )
    data = response.json()
    assert data["tool_used"] == "get_channel_comparison"


def test_chat_empty_message(mock_run_agent):
    mock_run_agent.return_value = {
        "response": "Please ask a question about traffic or revenue.",
        "tool_used": None,
    }
    response = client.post(
        "/api/v1/chat",
        json={"message": ""},
    )
    assert response.status_code == 200
    assert response.json()["tool_used"] is None


def test_chat_missing_message():
    response = client.post(
        "/api/v1/chat",
        json={},
    )
    assert response.status_code == 422


def test_chat_agent_error(mock_run_agent):
    mock_run_agent.side_effect = Exception("LLM unavailable")
    response = client.post(
        "/api/v1/chat",
        json={"message": "Which channel has the best performance?"},
    )
    assert response.status_code == 500
