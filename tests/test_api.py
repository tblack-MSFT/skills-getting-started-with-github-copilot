"""
Tests for the Mergington High School API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We have 9 predefined activities
        
        # Check that Chess Club exists and has correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_has_expected_activities(self, client, reset_activities):
        """Test that all expected activities are present."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_structure_is_correct(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the signup endpoint."""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity]["participants"])
        
        # Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        assert email in updated_activities[activity]["participants"]
        assert len(updated_activities[activity]["participants"]) == initial_participants + 1
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that signing up the same participant twice fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name and email."""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # URL encode the activity name and email
        encoded_activity = "Chess%20Club"
        encoded_email = "test%40mergington.edu"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]


class TestDeleteParticipantEndpoint:
    """Tests for the delete participant endpoint."""
    
    def test_delete_participant_successful(self, client, reset_activities):
        """Test successful removal of a participant."""
        email = "michael@mergington.edu"  # Existing participant in Chess Club
        activity = "Chess Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity]["participants"])
        
        # Remove participant
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        assert email not in updated_activities[activity]["participants"]
        assert len(updated_activities[activity]["participants"]) == initial_participants - 1
    
    def test_delete_nonexistent_participant(self, client, reset_activities):
        """Test removal of participant who is not signed up."""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_delete_from_nonexistent_activity(self, client, reset_activities):
        """Test removal from non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_delete_url_encoding(self, client, reset_activities):
        """Test delete with URL-encoded activity name and email."""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # URL encode the activity name and email
        encoded_activity = "Chess%20Club"
        encoded_email = "michael%40mergington.edu"
        
        response = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete user scenarios."""
    
    def test_signup_and_delete_workflow(self, client, reset_activities):
        """Test complete workflow: signup then delete."""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Step 1: Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Step 2: Delete
        delete_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        after_delete = client.get("/activities")
        assert email not in after_delete.json()[activity]["participants"]
        assert len(after_delete.json()[activity]["participants"]) == initial_count
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """Test signing up for multiple different activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Soccer Team", "Basketball Club", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        final_response = client.get("/activities")
        final_data = final_response.json()
        
        for activity in activities_to_join:
            assert email in final_data[activity]["participants"]
    
    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that participant counts are tracked correctly."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            participants_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            # Verify counts are logical
            assert participants_count >= 0
            assert max_participants > 0
            assert participants_count <= max_participants
