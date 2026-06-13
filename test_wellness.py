import unittest
import os
import json
import sqlite3
from unittest.mock import patch, MagicMock
import requests

# Set environment variables for tests
os.environ["GEMINI_API_KEY"] = "test-mock-api-key"

import database
from gemini_client import GeminiClient

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Point database to a temporary test DB
        cls.orig_db_name = database.DB_NAME
        database.DB_NAME = "test_wellness.db"

    @classmethod
    def tearDownClass(cls):
        # Restore database name
        database.DB_NAME = cls.orig_db_name
        # Delete temporary test DB file if it exists
        if os.path.exists("test_wellness.db"):
            try:
                os.remove("test_wellness.db")
            except PermissionError:
                pass

    def setUp(self):
        # Initialize fresh DB before each test
        if os.path.exists("test_wellness.db"):
            try:
                os.remove("test_wellness.db")
            except PermissionError:
                pass
        database.init_db()

    def test_database_initialization(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        self.assertIn("user_profile", tables)
        self.assertIn("journal_entries", tables)
        self.assertIn("chat_history", tables)
        
        conn.close()

    def test_profile_operations(self):
        # Test default profile row exists
        profile = database.get_profile()
        self.assertEqual(profile["target_exam"], "JEE")
        self.assertEqual(profile["study_hours"], 8.0)
        self.assertEqual(profile["main_stressor"], "Time Management")

        # Test updating profile
        database.save_profile("UPSC", 10.5, "Fear of Failure")
        profile = database.get_profile()
        self.assertEqual(profile["target_exam"], "UPSC")
        self.assertEqual(profile["study_hours"], 10.5)
        self.assertEqual(profile["main_stressor"], "Fear of Failure")

    def test_journal_operations(self):
        # Add journal logs
        database.add_journal_entry(
            date_str="2026-06-13",
            mood="Anxious",
            journal_text="I am stressed about the math mock exam tomorrow.",
            stress_level=7,
            emotions=["Anxiety", "Fear"],
            triggers=["Mock Test", "Time Limit"],
            empathy_note="Mock tests are stressful.",
            coping_strategy="Do box breathing.",
            mindfulness_prompt="Breath in."
        )

        entries = database.get_journal_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["mood"], "Anxious")
        self.assertEqual(entries[0]["stress_level"], 7)
        self.assertEqual(entries[0]["emotions"], ["Anxiety", "Fear"])
        self.assertEqual(entries[0]["triggers"], ["Mock Test", "Time Limit"])

        # Test entry deletion
        entry_id = entries[0]["id"]
        database.delete_journal_entry(entry_id)
        
        entries = database.get_journal_entries()
        self.assertEqual(len(entries), 0)

    def test_chat_operations(self):
        # Test adding messages
        database.add_chat_message("user", "Hello Aura")
        database.add_chat_message("assistant", "Hello! How can I support you?")

        history = database.get_chat_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello Aura")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hello! How can I support you?")

        # Test clearing history
        database.clear_chat_history()
        history = database.get_chat_history()
        self.assertEqual(len(history), 0)


class TestGeminiClient(unittest.TestCase):
    def setUp(self):
        self.client = GeminiClient(api_key="test-api-key")

    def test_configuration(self):
        self.assertTrue(self.client.is_configured())

    @patch("requests.post")
    def test_analyze_journal_entry_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "stress_level": 5,
                                    "emotions": ["Fatigue"],
                                    "triggers": ["Lack of Sleep"],
                                    "empathy_note": "Get some rest.",
                                    "coping_strategy": ["Sleep 8 hours"],
                                    "mindfulness_prompt": "Relax your jaw."
                                })
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Execute call
        result = self.client.analyze_journal_entry(
            journal_text="I am tired.",
            mood_emoji="😴",
            target_exam="GATE",
            current_stressor="Lack of Sleep"
        )

        # Assertions
        self.assertEqual(result["stress_level"], 5)
        self.assertEqual(result["emotions"], ["Fatigue"])
        self.assertEqual(result["triggers"], ["Lack of Sleep"])
        self.assertEqual(result["empathy_note"], "Get some rest.")
        self.assertEqual(result["coping_strategy"], ["Sleep 8 hours"])
        self.assertEqual(result["mindfulness_prompt"], "Relax your jaw.")
        
        # Verify correct headers and url payload
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("x-goog-api-key", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["x-goog-api-key"], "test-api-key")
        self.assertNotIn("key=", args[0])  # Key should not be in the query parameter URL

    @patch("requests.post")
    def test_generate_companion_response_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Hello Student, I am Aura."}]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        history = [{"role": "user", "content": "Hi"}]
        profile = {"target_exam": "NEET", "study_hours": 9.0, "main_stressor": "Syllabus"}
        
        res = self.client.generate_companion_response(history, profile, [])
        self.assertEqual(res, "Hello Student, I am Aura.")

    @patch("requests.post")
    def test_generate_wellness_report_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "### Report details"}]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        entries = [{
            "date": "2026-06-13",
            "mood": "Neutral",
            "stress_level": 4,
            "emotions": ["Neutral"],
            "triggers": ["None"],
            "journal_text": "Normal day."
        }]
        profile = {"target_exam": "JEE", "study_hours": 8.0, "main_stressor": "Mock Test"}
        
        res = self.client.generate_wellness_report(entries, profile)
        self.assertEqual(res, "### Report details")

    @patch("requests.post")
    def test_api_error_handling(self, mock_post):
        # Mock connection or HTTP error
        mock_post.side_effect = requests.exceptions.HTTPError("Bad Request")

        with self.assertRaises(Exception) as context:
            self.client.analyze_journal_entry("text", "emoji", "exam", "stressor")

        self.assertIn("Gemini API Error", str(context.exception))

if __name__ == "__main__":
    unittest.main()
