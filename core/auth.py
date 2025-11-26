from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import uuid
import json
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'users_db.json')

class AuthUser:
    def __init__(self, username, email, password):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.cv_data = None
        self.cv_filename = None
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'cv_filename': self.cv_filename
        }

def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = {}
                for user_id, user_data in data.items():
                    user = AuthUser.__new__(AuthUser)
                    user.id = user_data['id']
                    user.username = user_data['username']
                    user.email = user_data['email']
                    user.password_hash = user_data['password_hash']
                    user.cv_data = user_data.get('cv_data')
                    user.cv_filename = user_data.get('cv_filename')
                    users[user_id] = user
                return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    return {}

def _save_users(users_db):
    try:
        data = {}
        for user_id, user in users_db.items():
            data[user_id] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'cv_data': user.cv_data,
                'cv_filename': user.cv_filename
            }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"[SUCCESS] Users saved to {USERS_FILE}")
    except Exception as e:
        print(f"[ERROR] Error saving users: {e}")

USERS_DB = _load_users()

def reload_users_db():
    global USERS_DB
    USERS_DB = _load_users()

def register_user(username, email, password):
    global USERS_DB
    
    for user in USERS_DB.values():
        if user.username == username or user.email == email:
            return None, "Username or email already exists"
    
    user = AuthUser(username, email, password)
    USERS_DB[user.id] = user
    _save_users(USERS_DB)
    print(f"[SUCCESS] User registered: {user.username} (ID: {user.id})")
    return user, None

def login_user(username_or_email, password):
    global USERS_DB
    
    USERS_DB = _load_users()
    
    for user in USERS_DB.values():
        if (user.username == username_or_email or user.email == username_or_email):
            if user.check_password(password):
                print(f"[SUCCESS] User logged in: {user.username}")
                return user, None
    return None, "Invalid credentials"

def get_user_by_id(user_id):
    global USERS_DB
    
    user = USERS_DB.get(user_id)
    if user:
        return user
    
    USERS_DB = _load_users()
    return USERS_DB.get(user_id)

def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if is_logged_in():
        user_id = session.get('user_id')
        user = get_user_by_id(user_id)
        if not user:
            print(f"[ERROR] User not found for ID: {user_id}")
        return user
    return None

def logout_user():
    session.pop('user_id', None)
    session.pop('username', None)
