# auth.py
# Handles admin authentication for Student Management System

import hashlib
from database import Database


# -----------------------------
# Password hashing
# -----------------------------
def hash_password(password: str) -> str:
    """
    Convert plain password into SHA-256 hash
    """
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# Login function
# -----------------------------
def login(username: str, password: str) -> bool:
    """
    Validate admin login credentials against MySQL
    """

    if not username or not password:
        return False

    db = Database()

    try:
        if not db.connect():
            return False

        query = "SELECT password FROM admins WHERE username = %s"
        db.cursor.execute(query, (username,))
        result = db.cursor.fetchone()

        db.close_connection()

        if not result:
            return False

        stored_password = result[0]

        return stored_password == hash_password(password)

    except Exception as e:
        print("[LOGIN ERROR]", e)
        return False

    finally:
        db.close_connection()


# -----------------------------
# Create admin (setup helper)
# -----------------------------
def create_admin(username: str, password: str) -> bool:
    """
    Insert new admin with hashed password
    """

    db = Database()

    try:
        if not db.connect():
            return False

        hashed_pw = hash_password(password)

        query = "INSERT INTO admins (username, password) VALUES (%s, %s)"
        db.cursor.execute(query, (username, hashed_pw))

        db.connection.commit()

        return True

    except Exception as e:
        print("[CREATE ADMIN ERROR]", e)
        return False

    finally:
        db.close_connection()