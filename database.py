import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# SQLite database file
DB_FILE = 'voice_assistant.db'

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Commands history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, email, password):
    """Register new user with hashed password"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
        if cursor.fetchone():
            return False, "Email or username already exists"
        
        # Hash password and insert user
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        
        conn.commit()
        conn.close()
        return True, "User registered successfully"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(email, password):
    """Verify user credentials"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return False, None, "User not found"
        
        user_id, username, password_hash = user
        
        if check_password_hash(password_hash, password):
            return True, {"user_id": user_id, "username": username, "email": email}, "Login successful"
        else:
            return False, None, "Invalid password"
    except Exception as e:
        return False, None, f"Login error: {str(e)}"

def get_user_by_id(user_id):
    """Get user information by ID"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"user_id": user[0], "username": user[1], "email": user[2]}
        return None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None

def get_password_by_email(email):
    """Get password hash by email (for password suggestion - never return actual password)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def log_command(user_id, command, response):
    """Log a command and response to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO commands (user_id, command, response) VALUES (?, ?, ?)',
            (user_id, command, response)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging command: {str(e)}")
        return False

def get_user_history(user_id, limit=10):
    """Get user's command history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT command, response, timestamp FROM commands WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
            (user_id, limit)
        )
        
        history = cursor.fetchall()
        conn.close()
        
        return [{"command": h[0], "response": h[1], "timestamp": h[2]} for h in history]
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return []

def clear_user_history(user_id):
    """Clear user's command history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM commands WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        return False

# Initialize database when module is imported
init_database()