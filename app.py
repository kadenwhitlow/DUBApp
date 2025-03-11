from flask import Flask, render_template, url_for, request, redirect, flash, session
import json

app = Flask(__name__, template_folder='/Users/sarahchastain/Downloads/DUBApp-account_creation/Frontend/HTML', 
            static_folder='/Users/sarahchastain/Downloads/DUBApp-account_creation/Frontend')
app.secret_key = 'test'

db_file = "/Users/sarahchastain/Downloads/DUBApp-account_creation/DUBDatabaseFiles/users.json"

def load_users():
    """Load users from the JSON file."""
    try:
        with open(db_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    """Save users to the JSON file."""
    with open(db_file, "w") as file:
        json.dump(users, file, indent=4)

@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    users = load_users()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        
        # Check if username already exists
        if username in users:
            flash('Username taken.', 'error')
            return redirect(url_for('account_creation'))
        
        # Check if passwords match
        if password != repassword:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('account_creation'))
        
        # Store the new user
        users[username] = password  # In production, hash the password before storing
        save_users(users)
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))  # Redirect to login page after account creation
    
    return render_template('account_creation.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        # Check if user exists and password matches
        if username in users and users[username] == password:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('Home.html')  # Render Home.html after login

if __name__ == '__main__':
    app.run(debug=True)
