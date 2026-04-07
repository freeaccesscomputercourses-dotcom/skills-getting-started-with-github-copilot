import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


def test_get_activities(client):
    # Arrange - TestClient is set up via fixture

    # Act - Make GET request to /activities
    response = client.get("/activities")

    # Assert - Check response status and content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club


def test_signup_success(client):
    # Arrange - Choose an activity with available spots and no existing participants
    activity = "Basketball Team"
    email = "newstudent@example.com"

    # Act - Make POST request to signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert - Check success response
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}

    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_already_signed_up(client):
    # Arrange - Use an activity where the email is already signed up
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act - Attempt to signup again
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert - Check error response
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_activity_not_found(client):
    # Arrange - Use a non-existent activity
    activity = "Nonexistent Activity"
    email = "test@example.com"

    # Act - Attempt to signup for non-existent activity
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert - Check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_success(client):
    # Arrange - Use an activity with existing participants
    activity = "Programming Class"
    email = "emma@mergington.edu"  # Already in participants

    # Act - Make DELETE request to remove participant
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert - Check success response
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}

    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]


def test_remove_participant_not_signed_up(client):
    # Arrange - Use an activity and an email not signed up
    activity = "Basketball Team"
    email = "notsigned@example.com"

    # Act - Attempt to remove non-participant
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert - Check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found in this activity"}


def test_remove_participant_activity_not_found(client):
    # Arrange - Use a non-existent activity
    activity = "Nonexistent Activity"
    email = "test@example.com"

    # Act - Attempt to remove from non-existent activity
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert - Check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_root_redirect(client):
    # Arrange - No special setup needed

    # Act - Make GET request to root
    response = client.get("/")

    # Assert - Check redirect response
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"