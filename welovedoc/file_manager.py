from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database import get_db

def create_user(email, password):
    db = get_db()
    hashed_pw = generate_password_hash(password)
    try:
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                  (email, hashed_pw))
        db.commit()
        return True
    except:
        return False

def check_auth(email, password):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_data(user_id):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

def add_subscription(user_id, days):
    db = get_db()
    user = get_user_data(user_id)
    
    if user['subscription_end'] and user['subscription_end'] > datetime.now():
        new_end = user['subscription_end'] + timedelta(days=days)
    else:
        new_end = datetime.now() + timedelta(days=days)
    
    db.execute('UPDATE users SET subscription_end = ? WHERE id = ?',
              (new_end, user_id))
    db.commit()

def check_subscription(user_id):
    user = get_user_data(user_id)
    if not user:
        return False
    return user['subscription_end'] and user['subscription_end'] > datetime.now()