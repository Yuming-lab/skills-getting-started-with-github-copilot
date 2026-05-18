from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
BASE_ACTIVITIES = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = set(BASE_ACTIVITIES.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == expected_activity_names
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Art Studio"
    new_email = "teststudent@example.com"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_deletes_existing_participant():
    # Arrange
    activity_name = "Soccer Club"
    removable_email = "remove-test@example.com"
    if removable_email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(removable_email)
    assert removable_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": removable_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {removable_email} from {activity_name}"}
    assert removable_email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_400():
    # Arrange
    activity_name = "Science Club"
    missing_email = "missing@example.com"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
