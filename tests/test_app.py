"""
Backend API tests for the Mergington High School activities app.

All tests follow the AAA (Arrange-Act-Assert) pattern.
State isolation between tests is handled automatically by the
`reset_activities` autouse fixture in conftest.py.
"""


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestRoot:
    def test_redirects_to_static_index(self, client):
        # Arrange — no setup needed; root has no prerequisites

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self, client):
        # Arrange — no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_returns_dict_of_activities(self, client):
        # Arrange — no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_each_activity_has_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert required_fields.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_happy_path_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_happy_path_participant_appears_in_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_unknown_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_returns_400(self, client):
        # Arrange — michael is already seeded in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/participants
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_happy_path_removes_participant(self, client):
        # Arrange — michael is already seeded in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_happy_path_participant_absent_after_removal(self, client):
        # Arrange — michael is already seeded in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unknown_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_non_enrolled_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "noone@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"
