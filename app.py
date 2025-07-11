from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

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