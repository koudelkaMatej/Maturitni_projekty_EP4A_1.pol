import unittest
import os
import sqlite3
from data_manager import DataManager

TEST_DB_FILE = "tests/test_fitness.db"

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Inicializace čistého testovacího prostředí s dočasnou DB
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        self.dm = DataManager(db_file=TEST_DB_FILE)

    def tearDown(self):
        # Úklid po testech
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def test_add_user_and_login(self):
        """Testuje registraci a následné přihlášení uživatele."""
        username = "test_gym_rat"
        password = "secret_password"
        email = "test@gym.cz"

        # 1. Registrace
        success, msg = self.dm.add_user(username, password, email)
        self.assertTrue(success)
        self.assertEqual(msg, "Registrace úspěšná")

        # 2. Ověření duplicity
        success, msg = self.dm.add_user(username, password, email)
        self.assertFalse(success)
        self.assertEqual(msg, "Uživatel již existuje")

        # 3. Přihlášení (správné)
        self.assertTrue(self.dm.validate_login(username, password))

        # 4. Přihlášení (špatné heslo)
        self.assertFalse(self.dm.validate_login(username, "wrong_password"))

    def test_workout_persistence(self):
        """Testuje uložení tréninku a jeho správné načtení z DB přes JOINy."""
        username = "alex"
        self.dm.add_user(username, "1234", "alex@seznam.cz")
        
        workout_data = [
            ("Bench press", 3, 10, 60),
            ("Dřepy", 3, 8, 100)
        ]
        note = "Dneska to šlo skvěle!"
        
        # Uložení tréninku
        user_data = self.dm.save_workout(username, workout_data, note, "Summary text")
        
        # Ověření, že se trénink uložil
        self.assertEqual(len(user_data["workouts"]), 1)
        self.assertEqual(user_data["workouts"][0]["note"], note)
        
        # Ověření M:N vztahu (položky tréninku)
        exercises = user_data["workouts"][0]["exercises"]
        self.assertEqual(len(exercises), 2)
        self.assertEqual(exercises[0][0], "Bench press")
        self.assertEqual(exercises[1][3], 100)

    def test_personal_records(self):
        """Testuje automatický výpočet PR (MAX weight) v SQL."""
        username = "powerlifter"
        self.dm.add_user(username, "pass", "p@p.cz")
        
        # První trénink (60kg)
        self.dm.save_workout(username, [("Dřepy", 3, 5, 60)], "", "")
        
        # Druhý trénink (zlepšení na 80kg)
        user_data = self.dm.save_workout(username, [("Dřepy", 3, 5, 80)], "", "")
        
        # Ověření PR v načtených datech
        self.assertEqual(user_data["personal_records"]["Dřepy"], 80)

if __name__ == '__main__':
    unittest.main()
