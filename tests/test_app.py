from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_api_generate_workout():

    response = client.post(
        "/api/generate-workout",
        json={
            "user_id": "test001",
            "name": "Test User",
            "age": 20,
            "weight": 65,
            "goal": "Muscle Gain",
            "intensity": "Medium",
            "experience": "Beginner"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert "workout_plan" in data

    assert "nutrition_tip" in data


def test_get_user():

    response = client.get(
        "/api/users/test001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == "test001"


def test_feedback():

    response = client.post(
        "/api/submit-feedback",
        json={
            "user_id": "test001",
            "feedback": "Add more cardio and include yoga."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert "updated_plan" in data


def test_delete_user():

    response = client.delete(
        "/api/users/test001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True