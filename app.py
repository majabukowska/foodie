from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'foodie'

# Database setup
DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def create_table():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL)''')
    db.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(id=user['id'], name=user['name'], email=user['email'], password=user['password'])
    return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            flash('Sprawdź swoje dane logowania i spróbuj ponownie.')
            return redirect(url_for('login'))

        user_obj = User(id=user['id'], name=user['name'], email=user['email'], password=user['password'])
        login_user(user_obj)
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user:
            flash('Email już istnieje.')
            return redirect(url_for('signup'))

        db.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)',
                   (name, email, generate_password_hash(password)))
        db.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    create_table()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
