
import sqlite3
from pathlib import Path

DATABASE_NAME = Path(__file__).resolve().parent / "resolveai.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    print("Foreign keys enabled:", connection.execute("PRAGMA foreign_keys").fetchone()[0])

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL CHECK (
            role IN ('Employee', 'IT Technician', 'Administrator')
        )
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT,
        priority TEXT NOT NULL DEFAULT 'Medium' CHECK (
            priority IN ('Low', 'Medium', 'High', 'Critical')
        ),
        status TEXT NOT NULL DEFAULT 'Open' CHECK (
            status IN ('Open', 'In Progress', 'Pending', 'Resolved', 'Closed')
        ),
        submitted_by INTEGER NOT NULL,
        assigned_to INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (submitted_by) REFERENCES users(id),
        FOREIGN KEY (assigned_to) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users (name, email, role)
    VALUES (?, ?, ?)
    """, ("John Smith", "john@example.com", "Employee"))

    cursor.execute("""
    INSERT OR IGNORE INTO users (name, email, role)
    VALUES (?, ?, ?)
    """, ("Sarah Johnson", "sarah@example.com", "IT Technician"))

    cursor.execute("""
    SELECT id FROM tickets
    WHERE title = ? AND submitted_by = (
        SELECT id FROM users WHERE email = ?
    )
    """, ("VPN not connecting", "john@example.com"))

    existing_ticket = cursor.fetchone()

    if existing_ticket is None:
        cursor.execute("""
        INSERT INTO tickets (
            title,
            description,
            category,
            submitted_by
        )
        VALUES (?, ?, ?, ?)
        """, (
            "VPN not connecting",
            "Unable to connect to company VPN",
            "Network",
            cursor.execute(
                "SELECT id FROM users WHERE email = ?",
                ("john@example.com",)
            ).fetchone()[0]
        ))

    connection.commit()
    connection.close()

    print("ResolveAI database initialized successfully!")

if __name__ == "__main__":
    initialize_database()