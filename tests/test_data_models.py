"""
Tests for the data models and business logic of the activities system.
"""

import pytest
from src.app import activities


class TestActivitiesDataStructure:
    """Tests for the activities data structure."""
    
    def test_activities_is_dict(self, reset_activities):
        """Test that activities is a dictionary."""
        assert isinstance(activities, dict)
    
    def test_all_activities_have_required_fields(self, reset_activities):
        """Test that all activities have required fields."""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
    
    def test_participants_are_valid_emails(self, reset_activities):
        """Test that all participants have valid email format."""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert email_pattern.match(participant), f"Invalid email '{participant}' in '{activity_name}'"
    
    def test_max_participants_positive(self, reset_activities):
        """Test that max_participants is always positive."""
        for activity_name, activity_data in activities.items():
            assert activity_data["max_participants"] > 0, f"Activity '{activity_name}' has non-positive max_participants"
    
    def test_participants_within_limit(self, reset_activities):
        """Test that current participants don't exceed max_participants."""
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            assert current_count <= max_count, f"Activity '{activity_name}' exceeds participant limit"
    
    def test_no_duplicate_participants(self, reset_activities):
        """Test that there are no duplicate participants in any activity."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            assert len(participants) == len(unique_participants), f"Activity '{activity_name}' has duplicate participants"
    
    def test_descriptions_not_empty(self, reset_activities):
        """Test that all activity descriptions are not empty."""
        for activity_name, activity_data in activities.items():
            assert len(activity_data["description"]) > 0, f"Activity '{activity_name}' has empty description"
    
    def test_schedules_not_empty(self, reset_activities):
        """Test that all activity schedules are not empty."""
        for activity_name, activity_data in activities.items():
            assert len(activity_data["schedule"]) > 0, f"Activity '{activity_name}' has empty schedule"


class TestActivitiesBusinessLogic:
    """Tests for business logic related to activities."""
    
    def test_mergington_email_domain(self, reset_activities):
        """Test that all participants use mergington.edu email domain."""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert participant.endswith("@mergington.edu"), f"Participant '{participant}' in '{activity_name}' doesn't use school domain"
    
    def test_activity_types_coverage(self, reset_activities):
        """Test that we have good coverage of different activity types."""
        activity_names = list(activities.keys())
        
        # Check for different types of activities
        sports_activities = [name for name in activity_names if any(sport in name.lower() for sport in ["soccer", "basketball", "gym"])]
        academic_activities = [name for name in activity_names if any(academic in name.lower() for academic in ["chess", "programming", "math", "science"])]
        artistic_activities = [name for name in activity_names if any(art in name.lower() for art in ["art", "drama"])]
        
        assert len(sports_activities) > 0, "No sports activities found"
        assert len(academic_activities) > 0, "No academic activities found"
        assert len(artistic_activities) > 0, "No artistic activities found"
    
    def test_reasonable_participant_limits(self, reset_activities):
        """Test that participant limits are reasonable for high school activities."""
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            # Reasonable limits for high school activities (5-30 students)
            assert 5 <= max_participants <= 30, f"Activity '{activity_name}' has unreasonable participant limit: {max_participants}"
    
    def test_schedule_format_consistency(self, reset_activities):
        """Test that schedules follow a consistent format."""
        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]
            # Should contain day(s) and time information
            assert any(day in schedule for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]), f"Schedule for '{activity_name}' missing day information"
            assert any(time_indicator in schedule for time_indicator in ["AM", "PM", ":"]), f"Schedule for '{activity_name}' missing time information"


class TestDataConsistency:
    """Tests for data consistency across the application."""
    
    def test_activity_name_uniqueness(self, reset_activities):
        """Test that all activity names are unique."""
        activity_names = list(activities.keys())
        unique_names = set(activity_names)
        assert len(activity_names) == len(unique_names), "Duplicate activity names found"
    
    def test_participant_email_format_consistency(self, reset_activities):
        """Test that participant emails follow consistent naming pattern."""
        all_participants = []
        for activity_data in activities.values():
            all_participants.extend(activity_data["participants"])
        
        # Check that all emails follow the pattern: name@mergington.edu
        for email in all_participants:
            username = email.split("@")[0]
            assert username.isalpha(), f"Email username '{username}' contains non-alphabetic characters"
            assert len(username) >= 2, f"Email username '{username}' is too short"
    
    def test_total_enrollment_reasonable(self, reset_activities):
        """Test that total enrollment across all activities is reasonable."""
        all_participants = set()
        for activity_data in activities.values():
            all_participants.update(activity_data["participants"])
        
        # Assuming a high school might have 100-2000 students
        total_unique_participants = len(all_participants)
        assert 1 <= total_unique_participants <= 100, f"Total unique participants ({total_unique_participants}) seems unreasonable"