import sqlite3
from sqlite3 import Connection
import os
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to connect to the SQLite database (or create it if it doesn't exist)
def get_db_connection(db_name: str = "users.db") -> Connection:
    """
    Create a connection to the SQLite database.
    If the database does not exist, it will be created.
    """
    # Check if the database file exists
    if not os.path.exists(db_name):
        print(f"Database '{db_name}' not found. Creating a new one...")
    
    # Connect to the database (it will create the file if it doesn't exist)
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row  # This allows dictionary-like access to rows
    return connection

# Function to create the "users" table if it doesn't already exist
def create_users_table(connection: Connection):
    """
    Create a 'users' table in the SQLite database if it doesn't already exist.
    """
    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    print("Ensured 'users' table exists.")

# Function to log user information in the database
def log_user_info(full_name: str, username: str, email: str, plain_password: str, db_name: str = "users.db"):
    """
    Logs user information into the 'users' table in the SQLite database.

    Args:
        full_name (str): Full name of the user.
        username (str): Username of the user.
        email (str): Email of the user.
        plain_password (str): Plain text password of the user. It will be hashed before storing.
        db_name (str): Name of the SQLite database file (default is 'users.db').
    """
    # Connect to the database
    connection = get_db_connection(db_name)
    
    # Ensure the users table exists
    create_users_table(connection)
    
    # Hash the password
    hashed_password = pwd_context.hash(plain_password)
    
    try:
        # Insert user data into the 'users' table
        with connection:
            connection.execute(
                """
                INSERT INTO users (full_name, username, email, hashed_password)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, username, email, hashed_password),
            )
        print(f"User {username} logged successfully!")
    except sqlite3.IntegrityError as e:
        # Handle cases where the username or email already exists
        print(f"Error: {e}")
    finally:
        # Close the database connection
        connection.close()

# Function to authenticate a user
def check_user(username: str, plain_password: str, db_name: str = "users.db") -> dict:
    """
    Authenticates a user by verifying the username and password.
    If the user is valid, returns the user's information.

    Args:
        username (str): The username to authenticate.
        plain_password (str): The plain text password to verify.
        db_name (str): Name of the SQLite database file (default is 'users.db').

    Returns:
        dict: A dictionary containing the user's information (excluding the password) if authentication is successful.
        None: If authentication fails.
    """
    # Connect to the database
    connection = get_db_connection(db_name)
    
    try:
        # Fetch the user from the database
        cursor = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        
        if user:
            # Verify the password
            if pwd_context.verify(plain_password, user["hashed_password"]):
                # Return user information (excluding the hashed password)
                return {
                    "id": user["id"],
                    "full_name": user["full_name"],
                    "username": user["username"],
                    "email": user["email"],
                    # "created_at": user["created_at"]
                }
            else:
                print("Invalid password.")
        else:
            print("User not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        connection.close()
    
    # Authentication failed
    return None

def authenticate_user(username: str) -> bool:
    """
    Authenticates a user by verifying their username in the database.

    Args:
        username (str): The username to authenticate.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    connection = get_db_connection("users.db")
    try:
        cursor = connection.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user is not None
    except Exception as e:
        return False
        print(f"Error: {e}")
    finally:
        connection.close()

def add_or_update_lecture_data(db_name: str, data):
    """
    Add or update a lecture data in the database.

    Args:
        db (sqlite3.Connection): The database connection.
        data (Data): The data to add or update.
        
    """
    connection = get_db_connection(db_name)
    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                lecture TEXT NOT NULL,
                page TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL
            )
            """
        )

    try:
        # Insert user data into the 'users' table
        with connection:
            connection.execute(
                """
                INSERT INTO lectures (subject, lecture, page, data)
                VALUES (?, ?, ?, ?)
                """,
                (data.subject, data.lecture, data.page, data.data),
            )
        print(f"Data added successfully!")
    except sqlite3.IntegrityError as e:
        # Handle cases where the username or email already exists
        print(f"Error: {e}")
    finally:
        # Close the database connection
        connection.close()

# get lectures
def get_lecture_data(db_name: str, subject: str, lecture: str):
    """
    Retrieves a list of lecture data from the database that match the given subject and lecture.

    Args:
        db_name (str): The name of the SQLite database file.
        subject (str): The subject of the lecture.
        lecture (str): The title of the lecture.

    Returns:
        List[Dict[str, Union[str, int]]]: A list of dictionaries containing the page and data of the lecture if it exists, otherwise an empty list.
    """
    connection = get_db_connection(db_name)
    try:
        cursor = connection.execute("SELECT page, data FROM lectures WHERE subject = ? AND lecture = ?", (subject, lecture))
        rows = cursor.fetchall()
        if not rows:
            return []
        return [{"page": row[0], "data": row[1]} for row in rows]
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        connection.close()

# Example usage
if __name__ == "__main__":
    # Log a new user into the database
    full_name = "Haseeb Ahmad"
    username = "haseebahmad295"
    email = "quicktiptech@gmail.com"
    plain_password = "Haseeb543"

    # Log user info (this will create the user if it doesn't already exist)
    log_user_info(full_name, username, email, plain_password)

    # Authenticate the user
    print("\nAuthenticating user...")
    user_info = authenticate_user(username, plain_password)
    
    if user_info:
        print("Authentication successful!")
        print("User Info:", user_info)
    else:
        print("Authentication failed.")