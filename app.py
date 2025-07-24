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
                        capacity INTEGER,
                        location TEXT
                )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        location TEXT NOT NULL
                )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        org_name TEXT NOT NULL,
                        venue TEXT NOT NULL,
                        date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
                )
        """)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS reserved_equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id INTEGER,
                        equipment_id INTEGER,
                        quantity INTEGER,
                        FOREIGN KEY(event_id) REFERENCES event_history(id),
                        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
);
        """)
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            users = [
                ('admin', 'admin123', 'admin'),
                ('pasoa', 'pasoa123', 'org'),
                ('cs', 'cs123', 'org'),
                ('ms', 'ms123', 'org'),
                ('jpmap', 'jpmap123', 'org'),
                ('jma', 'jma123', 'org'),
                ('psme', 'psme123', 'org'),
                ('aeces', 'aeces123', 'org')
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
        
        with sqlite3.connect(DATABASE) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()

                cursor.execute("SELECT COUNT(*) FROM venues")
                total_venues = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT venue) FROM event_history WHERE date >= DATE('now')")
                used_venues = cursor.fetchone()[0]
                available_venues = total_venues - used_venues

                cursor.execute("SELECT SUM(quantity) FROM equipment")
                total_equipment = cursor.fetchone()[0] or 0

                cursor.execute("SELECT SUM(quantity) FROM reserved_equipment")
                used_equipment = cursor.fetchone()[0]

                available_equipment = total_equipment - used_equipment

        return render_template(
                "dashboard.html",
                used_venues=used_venues,
                available_venues=available_venues,
                used_equipment=used_equipment,
                available_equipment=available_equipment
        )

@app.route("/manage_venues")
def manage_venues():
        if 'user_id' not in session:
                return render_template(url_for('login'))
      
        with sqlite3.connect(DATABASE) as connection:
               connection.row_factory = sqlite3.Row
               cursor = connection.cursor()
               cursor.execute("SELECT * FROM venues")
               venues = cursor.fetchall()

        venue_list = []
        for row in venues:
                venue = dict(row)
                venue['is_available'] = True
                venue_list.append(venue)
               
        return render_template('manage_venues.html', venues=venues)

@app.route("/add_venue", methods=['POST'])
def add_venue():
        if 'user_id' not in session or session['role'] != 'admin':
            return redirect(url_for('login'))
      
        name = request.form['name']
        capacity = request.form['capacity']
        location = request.form['location']

        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                        INSERT INTO venues (name, capacity, location)
                        VALUES (?, ?, ?)
                """, (name, capacity, location))
                connection.commit()
        
        return redirect(url_for('manage_venues'))

@app.route("/edit_venue/<int:venue_id>", methods=['POST'])
def edit_venue(venue_id):
        if 'user_id' not in session or session['role'] != 'admin':
                return
        
        name = request.form['name']
        capacity = request.form['capacity']
        location = request.form['location']

        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                        UPDATE venues
                        SET name = ?, capacity = ?, location = ?
                        WHERE id = ?
                """, (name, capacity, location, venue_id))
                connection.commit()

        return redirect(url_for('manage_venues'))
        
@app.route("/delete_venue/<int:venue_id>", methods=['POST'])
def delete_venue(venue_id):
        if 'user_id' not in session or session['role'] != 'admin':
                return redirect(url_for('login'))
        
        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM venues WHERE id = ?", (venue_id,))
                connection.commit()

        return redirect(url_for('manage_venues'))

@app.route("/manage_equipments")
def manage_equipments():
        if 'user_id' not in session or session['role'] != 'admin':
               return redirect(url_for('login'))
        
        with sqlite3.connect(DATABASE) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM equipment")
                equipments = cursor.fetchall()

        return render_template('manage_equipments.html', equipments=equipments)


@app.route("/add_equipment", methods=['POST'])
def add_equipment():
        if 'user_id' not in session or session['role'] != 'admin':
                return redirect(url_for('login'))
        
        name = request.form['name']
        quantity = request.form['quantity']
        location = request.form['location']

        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                        INSERT INTO equipment (name, quantity, location)
                        VALUES (?, ?, ?)
                """, (name, quantity, location))
                connection.commit()

        return redirect(url_for('manage_equipments'))

@app.route("/edit_equipment/<int:equipment_id>", methods=['POST'])
def edit_equipment(equipment_id):
        if 'user_id' not in session or session['role'] != 'admin':
               return redirect(url_for('login'))
        
        name = request.form['name']
        quantity = request.form['quantity']
        location = request.form['location']

        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                        UPDATE equipment
                        SET name = ?, quantity = ?, location = ?
                        WHERE id = ?
                """, (name, quantity, location, equipment_id))
                connection.commit()
        
        return redirect(url_for('manage_equipments'))

@app.route("/delete_equipment/<int:equipment_id>", methods=['POST'])
def delete_equipment(equipment_id):
        if 'user_id' not in session or session['role'] != 'admin':
               return redirect(url_for('login'))
        
        with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
                connection.commit()

        return redirect(url_for('manage_equipments'))

@app.route("/event_history")
def event_history():
        if 'user_id' not in session or session['role'] != 'admin':
                return redirect(url_for('login'))
        
        with sqlite3.connect(DATABASE) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM event_history ORDER BY date DESC")
                events = cursor.fetchall()

        return render_template("event_history.html", events=events)

@app.route("/schedule_venue", methods=['GET', 'POST'])
def schedule_venue():
        if 'user_id' not in session or session['role'] != 'org':
                return redirect(url_for('login'))
        
        with sqlite3.connect(DATABASE) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()

                cursor.execute("SELECT * FROM venues")
                venues = cursor.fetchall()

                cursor.execute("SELECT * FROM equipment")
                equipments_raw  = cursor.fetchall()

                equipment = []
                for eq in equipments_raw:
                        total_qty = eq['quantity']

                        cursor.execute("""
                                SELECT SUM(quantity) FROM reserved_equipment
                                WHERE equipment_id = ?
                        """, (eq['id'],))
                        reserved_qty = cursor.fetchone()[0] or 0

                        available_qty = total_qty - reserved_qty

                        equipment.append({
                                'id': eq['id'],
                                'name': eq['name'],
                                'total_quantity': total_qty,
                                'available_quantity': available_qty
                        })

                if request.method == 'POST':
                        venue_id = request.form['venue_id']
                        event_date = request.form['event_date']

                        cursor.execute("SELECT name FROM venues WHERE id = ?", (venue_id,))
                        venue_row = cursor.fetchone()
                        if not venue_row:
                                return "Venue not found", 400
                        
                        venue_name = venue_row['name']

                        cursor.execute("""
                                INSERT INTO event_history (org_name, venue, date)
                                VALUES (?, ?, ?)
                        """, (session['username'], venue_name, event_date))

                        cursor.execute("SELECT last_insert_rowid()")
                        event_id = cursor.fetchone()[0]

                        for eq in equipment: 
                                qty_str = request.form.get(f'equipment_{eq["id"]}')
                                if qty_str:
                                        try:
                                                qty = int(qty_str)
                                                if 0 < qty <= eq["available_quantity"]:
                                                        cursor.execute("""
                                                                INSERT INTO reserved_equipment (event_id, equipment_id, quantity)
                                                                VALUES (?, ?, ?)
                                                        """, (event_id, eq["id"], qty))
                                        except ValueError:
                                              pass      

                        connection.commit()
                        return redirect(url_for('dashboard'))
        
        return render_template("schedule_venue.html", venues=venues, equipment=equipment)

@app.route("/logout")
def logout():
      session.clear()
      return redirect(url_for('login'))

init_db()

if __name__ == "__main__":
    app.run()