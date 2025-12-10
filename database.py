import sqlite3
from datetime import datetime, timedelta

DB_NAME = "smartlocker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: lockers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lockers (
            id INTEGER PRIMARY KEY,
            is_occupied BOOLEAN DEFAULT 0,
            door_closed BOOLEAN DEFAULT 1,
            otp_code TEXT,
            hardware_type TEXT DEFAULT 'pi',
            gpio_pin INTEGER,
            sensor_pin INTEGER,
            special_code TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table: otp_codes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            locker_id INTEGER,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (locker_id) REFERENCES lockers (id)
        )
    ''')

    # Table: delivery_users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pin_code TEXT NOT NULL UNIQUE
        )
    ''')

    # Initialize 32 lockers if they don't exist
    cursor.execute('SELECT count(*) FROM lockers')
    if cursor.fetchone()[0] == 0:
        # Default: lockers 1-22 use Pi GPIO, 23-32 use MCP
        pi_gpios = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8]
        pi_sensors = [7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23]
        
        for i in range(1, 33):
            if i <= 22:
                # Pi GPIO lockers
                gpio_pin = pi_gpios[i-1] if i-1 < len(pi_gpios) else 4
                sensor_pin = pi_sensors[i-1] if i-1 < len(pi_sensors) else 7
                cursor.execute('''INSERT INTO lockers 
                    (id, is_occupied, door_closed, hardware_type, gpio_pin, sensor_pin) 
                    VALUES (?, 0, 1, 'pi', ?, ?)''', (i, gpio_pin, sensor_pin))
            else:
                # MCP lockers
                mcp_pin = i - 23
                cursor.execute('''INSERT INTO lockers 
                    (id, is_occupied, door_closed, hardware_type, gpio_pin) 
                    VALUES (?, 0, 1, 'mcp', ?)''', (i, mcp_pin))
        print("Initialized 32 lockers.")

    # Initialize default delivery user if not exists
    cursor.execute('SELECT count(*) FROM delivery_users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO delivery_users (name, pin_code) VALUES (?, ?)', ('Admin', '1234'))
        print("Initialized default delivery user (PIN: 1234).")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
