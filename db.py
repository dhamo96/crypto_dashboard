import sqlite3
from config import Config

def get_conn():
    return sqlite3.connect(Config.DATABASE)

def create_tables():
    conn = get_conn()
    cr = conn.cursor()
    
    # Users table
    cr.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Portfolio table
    cr.execute('''
        CREATE TABLE IF NOT EXISTS portfolio(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coin TEXT,
            quantity REAL,
            buy_price REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Alerts table
    cr.execute('''
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coin TEXT,
            target_price REAL,
            triggered INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
create_tables()