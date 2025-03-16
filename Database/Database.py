import sqlite3
from cryptography.fernet import Fernet
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.key = None
        self.cipher_suite = None

    def connect(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def initialize(self):
        self.connect()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL,
                                is_sudo INTEGER NOT NULL)''')
        self.conn.commit()

    def add_user(self, username, password, is_sudo):
        encrypted_password = self.encrypt_password(password)
        self.cursor.execute('''INSERT INTO users (username, password, is_sudo)
                               VALUES (?, ?, ?)''', (username, encrypted_password, is_sudo))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute('''SELECT * FROM users WHERE username = ?''', (username,))
        return self.cursor.fetchone()

    def validate_user(self, username, password):
        user = self.get_user(username)
        if user and self.decrypt_password(user[2]) == password:
            return True
        return False

    def encrypt_password(self, password):
        if not self.cipher_suite:
            self.generate_key()
        return self.cipher_suite.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password):
        if not self.cipher_suite:
            self.generate_key()
        return self.cipher_suite.decrypt(encrypted_password.encode()).decode()

    def generate_key(self):
        key_file = 'key.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
        self.cipher_suite = Fernet(self.key)
