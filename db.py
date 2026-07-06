import os
import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Opens a new connection to the MySQL database using env vars."""
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        port=os.environ.get("MYSQLPORT"),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
    )


def create_checkpoints_table():
    """Creates the checkpoints table if it doesn't already exist. Safe to call every startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            handle VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rating INT,
            unique_problems_solved INT,
            weaknesses_json TEXT,
            strengths_json TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def save_checkpoint(handle, rating, unique_problems_solved, weaknesses, strengths):
    """
    Inserts a new checkpoint row for this handle.
    `rating` should already be an int (or None if unrated) — caller's responsibility
    to have handled the "Unrated" string case before calling this.
    `weaknesses` and `strengths` are the list-of-dicts from analyzer.py.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO checkpoints (handle, rating, unique_problems_solved, weaknesses_json, strengths_json)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            handle,
            rating,
            unique_problems_solved,
            json.dumps(weaknesses),
            json.dumps(strengths),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_last_two_checkpoints(handle):
    """
    Returns the two most recent checkpoints for this handle, newest first.
    Returns a list of 0, 1, or 2 dicts.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # rows come back as dicts, not tuples
    cursor.execute(
        """
        SELECT * FROM checkpoints
        WHERE handle = %s
        ORDER BY created_at DESC
        LIMIT 2
        """,
        (handle,),
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Parse the JSON text columns back into Python lists
    for row in rows:
        row["weaknesses"] = json.loads(row["weaknesses_json"])
        row["strengths"] = json.loads(row["strengths_json"])

    return rows