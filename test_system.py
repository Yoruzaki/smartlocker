import unittest
import os
from database import init_db, get_db_connection
from hardware import MockMCP23017

class TestSmartLocker(unittest.TestCase):
    def setUp(self):
        # Use a test DB
        self.test_db = "test_smartlocker.db"
        import database
        database.DB_NAME = self.test_db
        init_db()
        self.hw = MockMCP23017()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_hardware_mock(self):
        # Test initial state
        states = self.hw.get_all_lockers_states()
        self.assertTrue(states[1]) # Door closed (True)
        
        # Open locker
        self.hw.open_locker(1)
        self.assertFalse(self.hw.read_door_state(1)) # Door open (False)

    def test_database_init(self):
        conn = get_db_connection()
        count = conn.execute('SELECT count(*) FROM lockers').fetchone()[0]
        self.assertEqual(count, 16)
        conn.close()

if __name__ == '__main__':
    unittest.main()
