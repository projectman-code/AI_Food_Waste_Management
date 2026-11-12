import os
import sqlite3
from config import Config

def get_db():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Donor',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        food_name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity_kg REAL NOT NULL,
        expiry_date TEXT,
        location TEXT,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'Available',
        claimed_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(donor_id) REFERENCES users(id),
        FOREIGN KEY(claimed_by) REFERENCES users(id)
    );
    """)
    db.commit()
    db.close()
