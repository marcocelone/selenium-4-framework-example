"""
Database helper methods for the test framework.
Handles all interactions with the marcoai MySQL database.
"""
import mysql.connector
import utilities.custom_logger as cl
import logging
import os
from dotenv import load_dotenv

load_dotenv()

log = cl.customLogger(logging.DEBUG)


def _get_connection():
    required = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Check your .env file or environment."
        )
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def save_user(first_name: str, last_name: str, email: str, city: str = "Auto-Generated", age: int = 0) -> int:
    """
    Insert a new user into the Customers table.
    Returns the new user's id.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(id) FROM Customers")
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        full_name = f"{first_name} {last_name}"
        cursor.execute(
            "INSERT INTO Customers (id, name, city, age) VALUES (%s, %s, %s, %s)",
            (new_id, full_name, city, age)
        )
        conn.commit()
        log.info(f"[DB] Saved user: id={new_id}, name='{full_name}', email='{email}'")
        return new_id
    finally:
        cursor.close()
        conn.close()


def get_user_by_name(full_name: str) -> dict | None:
    """
    Fetch a user row from Customers by full name.
    Returns a dict with keys: id, name, city, age — or None if not found.
    """
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Customers WHERE name = %s", (full_name,))
        row = cursor.fetchone()
        log.info(f"[DB] get_user_by_name('{full_name}'): {row}")
        return row
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    """
    Fetch a user row from Customers by id.
    Returns a dict with keys: id, name, city, age — or None if not found.
    """
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Customers WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        log.info(f"[DB] get_user_by_id({user_id}): {row}")
        return row
    finally:
        cursor.close()
        conn.close()


def delete_user_by_id(user_id: int):
    """
    Delete a user from the Customers table by id.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Customers WHERE id = %s", (user_id,))
        conn.commit()
        log.info(f"[DB] Deleted user with id={user_id}")
    finally:
        cursor.close()
        conn.close()


def delete_user_by_name(full_name: str):
    """
    Delete a user from the Customers table by full name.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Customers WHERE name = %s", (full_name,))
        conn.commit()
        log.info(f"[DB] Deleted user with name='{full_name}'")
    finally:
        cursor.close()
        conn.close()


def user_exists(full_name: str) -> bool:
    """
    Check if a user exists in the Customers table by full name.
    """
    return get_user_by_name(full_name) is not None
