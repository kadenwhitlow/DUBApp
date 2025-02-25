from flask import Flask, jsonify, request, render_template, url_for, redirect, flash, session
from flask_restful import Resource, Api
import requests
import json
from functools import wraps

app = Flask(__name__, template_folder='/Users/kadenwhitlow/Downloads/DUBApp/Frontend/HTML', static_folder='/Users/kadenwhitlow/Downloads/DUBApp/Frontend')
app.secret_key = 'test'

def login_required(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'user' in session:
			return func(*args, **kwargs)
		else:
			flash('You need to log in first!', 'error')
			return redirect(url_for('login'))
	return wrapper
##########################################################################################################

#Get the user data from the database
def get_data(username):
	
	return {}

##########################################################################################################

# LOGIN CODE

# Check if a user exists
def user_exists(username):
	users = load_users()
	return username in users

# Load all users from users.json
def load_users():
	try:
		with open('users.json', 'r') as f:
			return json.load(f)
	except FileNotFoundError:
		return {}  

# Add new user
def add_user(username, password, interests):
	users = load_users()
	users[username] = {
		"password": password,
		"interests": interests
	}
	with open('users.json', 'w') as f:
		json.dump(users, f)
	
##########################################################################################################

@app.route('/', methods=['GET', 'POST'])
def login():	
	if request.method == 'POST':
		username = "1" #request.form['username']
		password = "1" #request.form['password']

		if user_exists(username): 
			users = load_users()
			if username in users and users[username]['password'] == password:
				session['user'] = username
				user_data = get_data(username)
				return redirect(url_for('home'))
			else:
				flash('Invalid username or password. Please try again!', 'error') 
				return render_template('login.html') 
			
		else:
			flash('User does not exist. Please sign up below!', 'error') 
			return render_template('login.html') 
	
	else:
		return render_template('login.html') 

def verify_login():
    
    return None

if __name__ == '__main__':
    app.run(debug=True)