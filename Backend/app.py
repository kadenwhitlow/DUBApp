from flask import Flask, jsonify, request, render_template, url_for, redirect, flash, session
from flask_restful import Resource, Api
import requests
import json
from functools import wraps
import datetime
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from DUBDatabaseFiles.DynamoDBClass import DynamoTable

DT = DynamoTable("DUBUsers")

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

# LOGIN CODE

# Check if a user exists
def user_exists(username):
    users = load_users()
    if username in users:
        return True
    else:
        return False

# Load all users from the dynamodb database
def load_users():
    users = {}
    for i in DT.returnAllTableItems():
        users[i['user_id']] = {
            'total_losses': i['total_losses'], 
            'current_bets': i['current_bets'], 
            'password': i['password'], 
            'account_balance': i['account_balance'], 
            'date_joined': i['date_joined'], 
            'previous_bets': i['previous_bets'], 
            'total_winnings': i['total_winnings']
        }
    
    return users

# Add new user
def add_user(username, password):
    DT.addUserToTable(username, password, datetime.datetime.now())
	
##########################################################################################################

@app.route('/', methods=['GET', 'POST'])
def login():	
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		if user_exists(username): 
			users = load_users()
			if users[username]['password'] == password:
				session['user'] = username
				return redirect(url_for('home'))
			else:
				flash('Invalid username or password. Please try again!', 'error') 
				return render_template('login.html') 
			
		else:
			flash('User does not exist. Please sign up below!', 'error')
			return render_template('login.html') 
	
	else:
		return render_template('login.html') 

@app.route("/home")
@login_required
def home():
    if "user" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))
    else:
        user_data = session["user"]  # Access user data
        return render_template("home.html", user=user_data)
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)