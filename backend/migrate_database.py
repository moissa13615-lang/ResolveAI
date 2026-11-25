
import sqlite3

DATABASE_NAME = "resolveai.db"

connection = sqlite3.connect(DATABASE_NAME)

connection.execute("PRAGMA foreign_keys = OFF")

cursor = connection.cursor()

try:
    cursor.execute("BEGIN TRANSACTION")

    cursor.execute("""
    CREATE TABLE users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL CHECK (
            role IN ('Employee', 'IT Technician', 'Administrator')
        )
    )
    """)

    cursor.execute("""
    INSERT INTO users_new (id, name, email, role)
    SELECT id, name, email, role
    FROM users
    """)

    cursor.execute("""
    CREATE TABLE tickets_new (
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
    INSERT INTO tickets_new (
        id,
        title,
        description,
        category,
        priority,
        status,
        submitted_by,
        assigned_to,
        created_at,
        updated_at
    )
    SELECT
        id,
        title,
        description,
        category,
        priority,
        status,
        submitted_by,
        assigned_to,
        created_at,
        updated_at
    FROM tickets
    """)

    cursor.execute("DROP TABLE tickets")
    cursor.execute("DROP TABLE users")

    cursor.execute("ALTER TABLE users_new RENAME TO users")
    cursor.execute("ALTER TABLE tickets_new RENAME TO tickets")

    violations = cursor.execute("PRAGMA foreign_key_check").fetchall()

    if violations:
        raise Exception("Migration failed: Foreign key violations found.")

    connection.commit()
    print("Database migration completed successfully!")

except Exception as error:
    connection.rollback()
    print("Migration failed:", error)
    raise

finally:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.close()
