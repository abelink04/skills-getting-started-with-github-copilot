import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to import path so that pytest can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["max_participants"] == 12


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate():
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_from_activity_success():
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_not_signed_up():
    # Arrange
    activity_name = "Gym Class"
    email = "notregistered@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]
