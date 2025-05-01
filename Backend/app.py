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
from flask import get_flashed_messages
from datetime import datetime
from Backend.results_verification import verify_results


DT = DynamoTable("DUBUsers")

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
    refresh_status()
    if "user" not in session:  # Extra safety check
        flash("You need to log in first!", "error")
        return redirect(url_for("login"))
    
    user_data = session["user"]
    return render_template("home.html", user=user_data)

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
    user_balance = users[session["user"]]["account_balance"]
    print(user_balance)

    bet_data = request.json.get('bet-list')

    bet_size = float(request.json.get('bet-size'))
    
    bet_parlay = request.json.get('parlay')
    
    if bet_size <= 0 or bet_size > user_balance:
        return jsonify({"error": "Invalid bet size. Check your balance."}), 400
    
    # makes sure bet_data is split properly
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
            'type_of_bet': bet_type,
            'bet_prop': bet_prop,
            'bet_odds': bet_odds,
            'bet_amount': bet_size,
            'player': player,
            'bet_status': 'pending'
        }
        bets_split.append(bet_dict)

    print("Placing bet....")
    print(f"PARLAY: {bets_split}")
    process_bet(bet_value, bets_split)

    return jsonify({"message": "Bets placed successfully.", "new_balance": user_balance})

def process_bet(bet_value, bet_list):
    if "user" in session:
        username = session["user"]
    print(users[username])
    DT.subtractBalanceFromTable(users[username]["account_balance"], users[username]["user_id"], bet_value)
    DT.addBetToTable(bet_list, users[username]["user_id"])
    
    return None

def refresh_status():
    # Call the API to get the latest scores and results
    GAME_DATABASE_RESPONSE = {
  "2025-04-04T17:00:00": {
    "91ca4289-3ab2-4458-8507-69f33ca8444a": {
      "date": "2025-04-04T17:00:00",
      "opponent": "Illinois State",
      "sport": "softball",
      "id": "91ca4289-3ab2-4458-8507-69f33ca8444a"
    }
  },
  "2025-04-05T14:00:00": {
    "8a0cde7a-991f-4ab9-8398-fb98b5991d03": {
      "date": "2025-04-05T14:00:00",
      "opponent": "Illinois State",
      "sport": "softball",
      "id": "8a0cde7a-991f-4ab9-8398-fb98b5991d03"
    },
    "caabecf3-186b-4d75-bd91-185ed7c2d0ad": {
      "date": "2025-04-05T14:00:00",
      "opponent": "Valparaiso",
      "sport": "womens-tennis",
      "id": "caabecf3-186b-4d75-bd91-185ed7c2d0ad"
    }
  },
  "2025-04-06T12:00:00": {
    "a2c1ec56-419d-4a48-a90b-2de972fcaf64": {
      "date": "2025-04-06T12:00:00",
      "opponent": "Illinois State",
      "sport": "softball",
      "id": "a2c1ec56-419d-4a48-a90b-2de972fcaf64"
    }
  },
  "2025-04-08T17:00:00": {
    "26522e90-6896-4db0-bc4a-71e4cb7a025a": {
      "date": "2025-04-08T17:00:00",
      "opponent": "UNI",
      "sport": "softball",
      "id": "26522e90-6896-4db0-bc4a-71e4cb7a025a"
    },
    "f0ec2b05-5eb1-4bd0-8f52-010b6c30f5d9": {
      "date": "2025-04-08T17:00:00",
      "opponent": "Omaha",
      "sport": "mens-tennis",
      "id": "f0ec2b05-5eb1-4bd0-8f52-010b6c30f5d9"
    }
  },
  "2025-04-09T15:00:00": {
    "43d5e1e4-8503-44d2-a795-1a2dd0370654": {
      "date": "2025-04-09T15:00:00",
      "opponent": "South Dakota",
      "sport": "softball",
      "id": "43d5e1e4-8503-44d2-a795-1a2dd0370654"
    }
  },
  "2025-04-09T17:00:00": {
    "df24675b-b4e4-4e42-a523-ac7c7c746fce": {
      "date": "2025-04-09T17:00:00",
      "opponent": "South Dakota",
      "sport": "softball",
      "id": "df24675b-b4e4-4e42-a523-ac7c7c746fce"
    }
  },
  "2025-04-11T17:00:00": {
    "65364a04-9bdc-47b9-b4bb-fb7c1f1a1c5c": {
      "date": "2025-04-11T17:00:00",
      "opponent": "Evansville",
      "sport": "softball",
      "id": "65364a04-9bdc-47b9-b4bb-fb7c1f1a1c5c"
    }
  },
  "2025-04-12T14:00:00": {
    "5acfb517-c863-4195-bf9f-b4458df0257d": {
      "date": "2025-04-12T14:00:00",
      "opponent": "Evansville",
      "sport": "softball",
      "id": "5acfb517-c863-4195-bf9f-b4458df0257d"
    },
    "9caa143e-fc4e-4430-bdd5-890d997651ef": {
      "date": "2025-04-12T14:00:00",
      "opponent": "UNI",
      "sport": "womens-tennis",
      "id": "9caa143e-fc4e-4430-bdd5-890d997651ef"
    }
  },
  "2025-04-13T12:00:00": {
    "5a47c8fa-e39c-40d2-a962-ef84e23d1d3b": {
      "date": "2025-04-13T12:00:00",
      "opponent": "Evansville",
      "sport": "softball",
      "id": "5a47c8fa-e39c-40d2-a962-ef84e23d1d3b"
    }
  },
  "2025-04-15T17:00:00": {
    "e03de3e4-ffbd-4fbd-9aca-9e6d500b96ad": {
      "date": "2025-04-15T17:00:00",
      "opponent": "UNI",
      "sport": "softball",
      "id": "e03de3e4-ffbd-4fbd-9aca-9e6d500b96ad"
    }
  },
  "2025-04-18T17:00:00": {
    "dc8d4123-624b-4827-afa2-972f38b8ea17": {
      "date": "2025-04-18T17:00:00",
      "opponent": "UIC",
      "sport": "softball",
      "id": "dc8d4123-624b-4827-afa2-972f38b8ea17"
    }
  },
  "2025-04-19T14:00:00": {
    "ea7c225e-a1e1-4217-975b-7643714b9cef": {
      "date": "2025-04-19T14:00:00",
      "opponent": "UIC",
      "sport": "softball",
      "id": "ea7c225e-a1e1-4217-975b-7643714b9cef"
    }
  },
  "2025-04-20T12:00:00": {
    "b2435532-cb01-4f40-92c6-1ad808ee86e3": {
      "date": "2025-04-20T12:00:00",
      "opponent": "UIC",
      "sport": "softball",
      "id": "b2435532-cb01-4f40-92c6-1ad808ee86e3"
        }
    },
}#requests.get("NONE").json()
    GAME_RESULTS_RESPONSE = [
        {
        'date': '2025-04-05T14:00:00', 
        'opponent': 'Illinois State', 
        'sport': 'softball', 
        'winner':  False, 
        'score': "4-5"
        },
        {
        'date': '2025-04-05T14:00:00', 
        'opponent': 'Valparaiso', 
        'sport': 'womens-tennis', 
        'winner':  True, 
        'score': "8-5"
        }
    ]#requests.get("NONE").json()
    
    
    # Check if a game is finished and update the status of the bet in the database
    if "user" in session:
        username = session["user"]
    formatted_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    user_data = DT.getItemFromTable(users[username]["user_id"])
    
    verified_results = verify_results(user_data, GAME_DATABASE_RESPONSE, GAME_RESULTS_RESPONSE, formatted_datetime)
    print(verified_results)
    #Create a loop that checks something like game_id, that we could store in the database and then also use to check the results
    #Once we check the ID if they match up and its finished we can update the bet status to won or lost and store finished
    
    for i in user_data['current_bets']:
        for m in i:
            if m['game_id'] in verified_results:
                total_bet = m
                total_bet['verified_results'] = verified_results[m['game_id']]
                print(total_bet)
            #if total_bet['verified_results']['bet_status'] == "win" or total_bet['verified_results']['bet_status'] == "loss":
                #DT.updateBetStatus(users[username]["user_id"], total_bet)
        
    return None

if __name__ == '__main__':
    app.run(debug=True)