from flask import Flask, jsonify, request, render_template, url_for, redirect, flash, session
from flask_restful import Resource, Api
import requests
import json
from functools import wraps
import datetime
from decimal import Decimal
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from DUBDatabaseFiles.DynamoDBClass import DynamoTable
from generatePoints import GeneratePoints
#from topBets import TopBets


from flask import get_flashed_messages
from datetime import datetime
from Backend.results_verification import verify_results

from datetime import datetime, timezone
from webscraping import WebScraper

DT = DynamoTable("DUBUsers")
DS = DynamoTable("DUBStorage")
#point_dist = GeneratePoints()


app = Flask(__name__, template_folder='/Users/kadenwhitlow/Downloads/DUBApp/Frontend/HTML', static_folder='/Users/kadenwhitlow/Downloads/DUBApp/Frontend')
app.secret_key = 'test'

#The login required function, which requires users to be logged in before accessing other pages and functions
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
            'total_winnings': i['total_winnings'],
            'email': i['email'],
            'user_id': i['user_id'],
        }
    
    return users

#LOAD THE USERS
users = load_users()



# Add new user
def add_user(username, password, email):
    DT.addUserToTable(username, password, email, datetime.datetime.now().isoformat())
	
##########################################################################################################

#Route and function that is used for our login page
@app.route('/', methods=['GET', 'POST'])
def login():	
    users = load_users()
    print("Rendering login page")  # Debugging
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if user_exists(username): 
            if users[username]['password'] == password:
                session['user'] = username
                return redirect(url_for('home'))
            else:
                session.modified = True  # Ensures Flask updates session
                flash('Invalid username or password. Please try again!', 'error') 
                messages = get_flashed_messages(with_categories=True)
                print(messages)  # Debug: See if messages exist
                return render_template('login.html') 
        
        else:
            flash('User does not exist. Please sign up below!', 'error')
            return render_template('login.html') 
    else:
        return render_template('login.html') 
    
#Route and function that is used for the account creation page
@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    users = load_users()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        email = request.form['email']
        
        # Check if username already exists
        if username in users:
            flash('Username taken.', 'error')
            return redirect(url_for('account_creation'))
        
        # Check if passwords match
        if password != repassword:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('account_creation'))
        
        # Store the new user
        add_user(username, password, email)
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))  # Redirect to login page after account creation
    
    return render_template('account_creation.html')

#Route and function that is used for our home page
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if "user" not in session:  # Extra safety check
        flash("You need to log in first!", "error")
        return redirect(url_for("login"))
    
    username = session["user"]
    user_data = DT.getItemFromTable(users[username]["user_id"])
    game_dict = DS.getItemFromTableStorage("games_storage")
    
    #top_bets_obj = TopBets(DT)
    #popular_bets = top_bets_obj.get_top_bets()
    print(game_dict)
    return render_template("home.html", user=user_data, data=game_dict, popular_bets=None)

#Route and function that is used to update and view the balance of a users account
@app.route("/balance")
def balance():
    if "user" in session:
        username = session["user"]
    if username in users:
        return jsonify({"balance": users[username]["account_balance"]})
    
    return jsonify({"balance": "N/A"})




@app.route('/place_bets', methods=['POST'])
def place_bets():
    print("Request JSON:", request.json)
    user_balance = Decimal(str(users[session["user"]]["account_balance"]))
    print(user_balance)

    bet_data = request.json.get('bet-list')
    bet_size = Decimal(str(request.json.get('bet-size')))
    bet_parlay = request.json.get('parlay')

    if bet_size <= 0 or bet_size > user_balance:
        return jsonify({"error": "Invalid bet size. Check your balance."}), 400

    bets_split = []
    for i in bet_data:
        bet_details = i.split("-")
        cleaned_bet_details = [item.strip() for item in bet_details]
        bet_value = cleaned_bet_details[0]
        bet_prop = cleaned_bet_details[1]
        player = cleaned_bet_details[2]
        bet_type, bet_odds = bet_data[-1].rsplit(" ", 1)
        bet_dict = {
            'bet_value': bet_value,
            'type_of_bet': bet_prop.lower(),
            'bet_prop': bet_prop,
            'bet_odds': bet_odds,
            'bet_amount': bet_size,
            'player': player,
            'bet_status': 'pending'
        }
        bets_split.append(bet_dict)

    print("Placing bet....")
    print(f"PARLAY: {bets_split}")
    process_bet(bet_size, bets_split)

    return jsonify({"message": "Bets placed successfully.", "new_balance": float(user_balance)})


def process_bet(bet_amount, bet_list):
    if "user" in session:
        username = session["user"]
    DT.subtractBalanceFromTable(users[username]["account_balance"], users[username]["user_id"], bet_amount)
    DT.addBetToTable(bet_list, users[username]["user_id"])
    
    return None


def games_dict(GAME_DATABASE_RESPONSE, date):
    WS = WebScraper()
    final_dict = {}
    for i in GAME_DATABASE_RESPONSE[date]:
        final_dict = WS.update_score(i)
    return final_dict

def refresh_status():
    # Call the API to get the latest scores and results
    WS = WebScraper()
    GAME_DATABASE_RESPONSE = None #requests.get("NONE").json()
    GAME_RESULTS_RESPONSE = games_dict(GAME_DATABASE_RESPONSE)
    
    
    # Check if a game is finished and update the status of the bet in the database
    if "user" in session:
        username = session["user"]
    else:
        return None  # No user logged in

    formatted_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    user_data = DT.getItemFromTable(users[username]["user_id"])

    verified_results = verify_results(user_data, GAME_DATABASE_RESPONSE, GAME_RESULTS_RESPONSE, formatted_datetime)
    print("Verified Results:", verified_results)

    updated_bets = []
    for bet_group in user_data['current_bets']:
        for bet in bet_group:
            game_id = bet.get('game_id')
            if game_id in verified_results:
                bet['verified_results'] = verified_results[game_id]
                print("Updating Bet:", bet)
                if bet['verified_results']['bet_status'] in ["win", "loss"]:
                    updated_bets.append(bet)

    for bet in updated_bets:

        DT.updateBetStatus(users[username]['user_id'], bet, user_data['account_balance'])
        
    return None

##########################################################################################################

#API and Webscraping
"""
The home screen should use: upcoming_schedule()
To calculate daily betting: game_today() gives list of games today then give list to betting() to have the
same list returned with betting information for each game. The time period could be adjusted. 
"""
@app.route('/official-bets')
def officialBets():

    #Pull a week worth of data, add the values to a list of dicitionaries
    game_data = DS.getItemFromTableStorage("games_storage")
	
    return render_template("official_bets.html", data = game_data)

@app.route('/my-bets')
def myBets():
    
    if "user" in session:
        username = session["user"]
    
    user_data = DT.getItemFromTable(users[username]["user_id"])
    
    my_bets = []
    for i in user_data["current_bets"]:
        my_bets.append(i)
    #the database just gave back filler data
    return render_template("My_Bets.html", data = my_bets)

if __name__ == '__main__':
    app.run(debug=True)
