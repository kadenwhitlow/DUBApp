from flask import Flask, jsonify, request, render_template, url_for, redirect, flash, session
from flask_restful import Resource, Api
import requests
import json
from functools import wraps
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from DUBDatabaseFiles.DynamoDBClass import DynamoTable
from flask import get_flashed_messages
from bs4 import BeautifulSoup
from datetime import datetime, timezone

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
        {
            'bet_value': bet_value,
            'type_of_bet': bet_type,
            'bet_prop': bet_prop,
            'bet_odds': bet_odds,
            'player': player,
        }
        bets_split.append(cleaned_bet_details)

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

##########################################################################################################

#API and Webscraping
"""
The home screen should use: upcoming_schedule()
To calculate daily betting: game_today() gives list of games today then give list to betting() to have the
same list returned with betting information for each game. The time period could be adjusted. 
"""

def date_converter(game_information): 
    date_list = game_information[1].split()
    if len(date_list) < 3:
        date_list.append("12:00")
        date_list.append("AM")

    if date_list[-1] == "TBD":
        date_list[-1] = "12:00"
        date_list.append("AM")

    if len(date_list[-2] ) < 3:
        date_list[-2] = date_list[-2] + ":00"
    
    date_list.append("2025")
    date_list = " ".join(date_list)

    game_date = date_list
    date_obj = datetime.strptime(game_date, "%B %d %I:%M %p %Y")
    
    current_utc_time = str(datetime.now(timezone.utc))
    current_utc_time = datetime.fromisoformat(current_utc_time).replace(tzinfo=None)

    return date_obj, current_utc_time

def scrape(link):
    response = requests.get(link)
    response_text = response.text
    soup = BeautifulSoup(response_text, 'html.parser')
    info = soup.find_all("div", class_="sidearm-schedule-game-opponent-name")
    info2 = soup.find_all("div", class_ = "sidearm-schedule-game-result text-italic")
    history_link = soup.find_all("li", class_ = "sidearm-schedule-game-links-opponent-history")

    return info, info2, history_link
        
def upcoming_schedule():
    game_list = []
    schedule_links = ["https://godrakebulldogs.com/sports/softball/schedule",
    "https://godrakebulldogs.com/sports/mens-tennis/schedule",
    "https://godrakebulldogs.com/sports/mens-soccer/schedule",
    "https://godrakebulldogs.com/sports/womens-soccer/schedule",
    "https://godrakebulldogs.com/sports/womens-tennis/schedule"]

    for x in schedule_links:
        info, _, _ = scrape(x)
        
        for i in range(len(info)):
            game_data = {}
            
            if info[i].find("a") != None:
                game_information = info[i].find("a")['aria-label'].split(" on ", 1)
                

                date_obj, current_utc_time = date_converter(game_information)

                if date_obj >= current_utc_time:
                    
                    game_data["date"] = date_obj.isoformat()
                    game_data["opponent"] = game_information[0]
                    game_data["sport"] = x.replace("https://godrakebulldogs.com/sports/", "").replace("/schedule", "")

                    game_list.append(game_data)
    return game_list

def link_organizer(game_dict):
    if game_dict["sport"] == "softball":
        schedule_link = "https://godrakebulldogs.com/sports/softball/schedule"

    elif game_dict["sport"] == "mens-tennis":
        schedule_link = "https://godrakebulldogs.com/sports/mens-tennis/schedule"

    elif game_dict["sport"] == "mens_soccer":
        schedule_link = "https://godrakebulldogs.com/sports/mens-soccer/schedule"

    elif game_dict["sport"] == "womens-soccer":
        schedule_link = "https://godrakebulldogs.com/sports/womens-soccer/schedule"

    elif game_dict["sport"] == "womens-tennis":
        schedule_link = "https://godrakebulldogs.com/sports/womens-tennis/schedule"

    return schedule_link

def update_score(game_dict):
    
    schedule_link = link_organizer(game_dict)

    info, info2, _ = scrape(schedule_link)

    for i in range(len(info)):
        game_data = {}
        
        if info[i].find("a") != None:
            game_information = info[i].find("a")['aria-label'].split(" on ", 1)
            
            date_obj, current_utc_time = date_converter(game_information)

            game_date = datetime.fromisoformat(game_dict["date"])

            if date_obj == game_date and game_information[0] == game_dict["opponent"]:
                
                game_data["date"] = date_obj.isoformat()
                game_data["opponent"] = game_information[0]
                game_data["sport"] = schedule_link.replace("https://godrakebulldogs.com/sports/", "").replace("/schedule", "")

                if i < len(info2):
                    span = info2[i].find_all("span")
                    
                    if len(span) > 3:
                        game_data["winner"] = span[1].get_text().replace(",", "")
                        game_data["score"] = span[2].get_text()
                    else:
                        game_data["winner"] = None
                        game_data["score"] = None

                else:
                    game_data["winner"] = None
                    game_data["score"] = None
                
                break

    return game_data

def game_today():
    today_list = []
    game_data = upcoming_schedule()

    current_utc_time = str(datetime.now(timezone.utc))
    current_utc_time = datetime.fromisoformat(current_utc_time).replace(tzinfo=None)

    for i in game_data:
        if datetime.fromisoformat(i["date"]).date() == current_utc_time.date():
            today_list.append(i)

    return today_list

def betting(game_dict):
    today_game_betting = []

    for y in game_dict:
        schedule_link = link_organizer(y)

        info, info2, history_links = scrape(schedule_link)
        
        drake_total = 0
        game_counter = 0

        for i in info2:

            span = i.find_all("span")
            score = span[2].get_text()
            score = score.split("-")

            drake_total += int(score[0])
            game_counter += 1

        drake_avg_ppg = drake_total / game_counter
        
        all_links = []
        for i in history_links:
            html_link = i.find("a")
            link = html_link.get("href")
            all_links.append(link)

        for i in range(len(info)):
                    
            if info[i].find("a") != None:
                game_information = info[i].find("a")['aria-label'].split(" on ", 1)
                
                date_obj, current_utc_time = date_converter(game_information)

                game_date = datetime.fromisoformat(y["date"])

                if date_obj == game_date and game_information[0] == y["opponent"]:
                    crawl_link = "https://godrakebulldogs.com" + all_links[i]
                    
                    response = requests.get(crawl_link)
                    response_text = response.text
                    soup = BeautifulSoup(response_text, 'html.parser')

                    stats = soup.find_all("div", "sidearm-opponent-history__item")
                    
                    for i in stats:
                        headline = i.find("h2")
                        headline = headline.get_text()
                        
                        if headline == "Home Record":
                            opponent_info = i.find("div", class_= "sidearm-opponent-history__item--number")
                            home_record = opponent_info.get_text().strip()
                            home_record = home_record.split("-")

                        elif headline == "Away Record":
                            opponent_info = i.find("div", class_= "sidearm-opponent-history__item--number")
                            away_record = opponent_info.get_text().strip()
                            away_record = away_record.split("-")

                        elif "Average" in headline:
                            opponent_info = i.find("div", class_= "sidearm-opponent-history__item--number")
                            average = opponent_info.get_text().strip()
                        
                    game_data = {}

                    game_data["home_data"] = {
                        "Wins" : int(home_record[0]),
                        "Losses" : int(home_record[1]),
                        "PPG" : drake_avg_ppg
                    }

                    game_data["away_data"] = {
                        "Wins" : int(away_record[0]),
                        "Losses" : int(away_record[1]),
                        "PPG" : float(average)
                    }

                    ml = mLineGenerator(game_data)
                    spread = spreadGenerator(game_data)
                    overUnder = overUnderGenerator(game_data)

                    y["betting"] = {
                        "ml" : ml,
                        "spread" : spread["spread"],
                        "overUnder" : overUnder["over_under"]
                    }

                    today_game_betting.append(y)

                    return today_game_betting

def mLineGenerator(game_data):
    home_win_perc = game_data['home_data']['Wins'] / (game_data['home_data']['Wins'] + game_data['home_data']['Losses'])
    away_win_perc = game_data['away_data']['Wins'] / (game_data['away_data']['Wins'] + game_data['away_data']['Losses'])
    
    if home_win_perc > away_win_perc:
        difference = (home_win_perc - away_win_perc) * 100
        away_ml = round(difference * 10)
        home_ml = round((difference + 11.37) * 10)
        return {'home_ml': f"-{home_ml}", 'away_ml': f"+{away_ml}"}
    else:
        difference = (away_win_perc - home_win_perc) * 100
        home_ml = round(difference * 10)
        away_ml = round((difference + 11.37) * 10)
        return {'home_ml': f"+{home_ml}", 'away_ml': f"-{away_ml}"}

def spreadGenerator(game_data):
    home_avg_spread = abs(game_data['home_data']['PPG'])
    away_avg_spread = abs(game_data['away_data']['PPG'])
    combined_average_spread = (home_avg_spread + away_avg_spread) / 2
    return {'spread': round(combined_average_spread)}

def overUnderGenerator(game_data):
    return {'over_under': round(game_data['home_data']['PPG'] + game_data['away_data']['PPG'])}


##########################################################################################################
if __name__ == '__main__':
    app.run(debug=True)