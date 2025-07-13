from flask import Flask, request, jsonify, url_for, render_template, session, redirect
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DATABASE = "event_tracker.db"

def init_db():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       role TEXT NOT NULL CHECK(role IN ('admin', 'org'))
                )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS venues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT
                )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        venue_id INTEGER,
                        date TEXT,
                        org_id TEXT,
                        equipment TEXT,
                        FOREIGN KEY (venue_id) REFERENCES venues(id),
                        FOREIGN KEY (org_id) REFERENCES users(id)
                )
        """)
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            users = [
                ('admin', 'admin123', 'admin'),
                ('bsoa', 'bsoa123', 'org'),
                ('domt', 'domt123', 'org'),
                ('bsit', 'bsit123', 'org'),
                ('dit', 'dit123', 'org'),
                ('bsedm', 'bsedm123', 'org'),
                ('bsede', 'bsede123', 'org'),
                ('bsbahrm', 'bsbahrm123', 'org'),
                ('bsbamm', 'bsbamm123', 'org'),
                ('bsme', 'bsme123', 'org'),
                ('bsece', 'bsece123', 'org')
            ]
            cursor.executemany("""
                    INSERT INTO users (username, password, role) 
                    VALUES (?, ?, ?)
            """, users)

        connection.commit()
        print("Database and tables initialized successfully")

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
        error = None
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']

                with sqlite3.connect(DATABASE) as connection:
                        cursor = connection.cursor()
                        cursor.execute("""
                                SELECT * FROM users 
                                WHERE username = ? AND password = ?
                        """, (username, password))
                        user = cursor.fetchone()

                        if user:
                                session['user_id'] = user[0]
                                session['username'] = user[1]
                                session['role'] = user[3]
                                return redirect(url_for('dashboard'))
                        else:
                                error = "Invalid username or password"
        
        return render_template('login.html', error=error)

@app.route("/dashboard")
def dashboard():
      if 'user_id' not in session:
            return redirect(url_for('login'))
      return render_template("dashboard.html")

@app.route("/logout")
def logout():
      session.clear()
      return redirect(url_for('login'))

init_db()

if __name__ == "__main__":
    app.run()