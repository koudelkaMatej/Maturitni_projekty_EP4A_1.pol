import unittest
import os
import json
import shutil
from data_manager import DataManager

TEST_DATA_DIR = "tests/data"
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, "test_users.json")

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Create a clean test environment
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        self.dm = DataManager(data_file=TEST_DATA_FILE)

    def tearDown(self):
        # Clean up
        if os.path.exists(TEST_DATA_DIR):
            shutil.rmtree(TEST_DATA_DIR)

    def test_save_and_load_workout(self):
        username = "testuser"
        workout_data = [
            ("Bench press", 3, 10, 60),
            ("Squat", 3, 8, 80)
        ]
        note = "Great workout"
        summary = "Bench press - 3x10, 60kg\nSquat - 3x8, 80kg"

        # Save workout
        updated_data = self.dm.save_workout(username, workout_data, note, summary)

        # Verify returned data
        self.assertIn("personal_records", updated_data)
        self.assertEqual(updated_data["personal_records"]["Bench press"], 60)
        self.assertEqual(updated_data["personal_records"]["Squat"], 80)

        # Verify file content
        loaded_data = self.dm.get_user_data(username)
        self.assertEqual(len(loaded_data["workouts"]), 1)
        self.assertEqual(loaded_data["workouts"][0]["note"], note)
        self.assertEqual(loaded_data["workouts"][0]["exercises"], [list(w) for w in workout_data])

    def test_progress_update(self):
        username = "testuser"
        # First workout
        workout1 = [("Bench press", 3, 10, 60)]
        self.dm.save_workout(username, workout1, "", "")

        # Second workout (progress)
        workout2 = [("Bench press", 3, 10, 65)]
        updated_data = self.dm.save_workout(username, workout2, "", "")

        # Verify PR update
        self.assertEqual(updated_data["personal_records"]["Bench press"], 65)

        # Verify progress history
        progress = updated_data["progress_data"]["Bench press"]
        self.assertEqual(len(progress), 2)
        self.assertEqual(progress[0]["weight"], 60)
        self.assertEqual(progress[1]["weight"], 65)

if __name__ == '__main__':
    unittest.main()
