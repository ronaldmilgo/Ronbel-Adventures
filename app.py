from flask import Flask, request, render_template, redirect, url_for, flash, session
import csv
import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the database from CSV
with open('database.csv', 'r') as file:
    database = list(csv.DictReader(file))



# Database initialization
def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)
        conn.commit()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        # Check if the username is already in the database
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE name = ?", (username,))
            if cur.fetchone():
                flash("Username already exists. Please choose a different one.")
                return redirect(url_for('signup'))

            # Insert new user into the database
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        (username, email, password))  # Password should be hashed
            conn.commit()

        # Redirect to the login page after successful signup
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check the username and password against the database
        with sqlite3.connect('users.db') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE name = ?", (username,))
            user = cur.fetchone()
            if user and user['password'] == password:
                session['username'] = username  # Save the username in the session
                return redirect(url_for('homepage'))
            else:
                flash("Invalid username or password")
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    username = session.get('username', 'Guest')
    return render_template('index.html', name=username)

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/inquiry')
def inquiry():
    return render_template('inquiry.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    # Your questionnaire logic goes here
    return render_template('questionnaire.html')  # Assuming you want to render the questionnaire form

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommendations', methods=['POST'])
def recommendations():
    # Retrieve form data
    feature = request.form['features']
    continent_ = request.form['continent']
    cost_range = request.form['costRange']


    cost_ranges = {
        "Below 1500": (0, 1500),
        "1500-1750": (1500, 1750),
        "1750-2000": (1750, 2000),
        "Above 2000": (2000, float('inf'))  # Assuming 'inf' represents a very high cost
    }

    # Filter destinations based on user preferences
    filtered_destinations = [
        destination for destination in database
        if (
            (not feature or feature in destination['features']) and
            (not continent_ or continent_ in destination['continent']) and
            (not cost_range or (cost_ranges[cost_range][0] <= int(destination['cost']) < cost_ranges[cost_range][1]))  # Filter based on cost range
        )
    ]



    return render_template('recommendations.html', destinations=filtered_destinations)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


