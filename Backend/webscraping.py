from bs4 import BeautifulSoup
import requests
from datetime import datetime, timezone
import uuid
import json

class WebScraper():
    def date_converter(self, game_information): 
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

    def scrape(self, link):
        response = requests.get(link)
        response_text = response.text
        soup = BeautifulSoup(response_text, 'html.parser')
        info = soup.find_all("div", class_="sidearm-schedule-game-opponent-name")
        info2 = soup.find_all("div", class_ = "sidearm-schedule-game-result text-italic")
        history_link = soup.find_all("li", class_ = "sidearm-schedule-game-links-opponent-history")

        return info, info2, history_link
            
    def upcoming_schedule(self):
        all_games = {}
        schedule_links = ["https://godrakebulldogs.com/sports/softball/schedule",
        "https://godrakebulldogs.com/sports/mens-tennis/schedule",
        "https://godrakebulldogs.com/sports/mens-soccer/schedule",
        "https://godrakebulldogs.com/sports/womens-soccer/schedule",
        "https://godrakebulldogs.com/sports/womens-tennis/schedule"]

        for x in schedule_links:
            info, _, _ = self.scrape(x)
            
            for i in range(len(info)):
                game_data = {}
                
                if info[i].find("a") != None:
                    game_information = info[i].find("a")['aria-label'].split(" on ", 1)
                    

                    date_obj, current_utc_time = self.date_converter(game_information)

                    if date_obj >= current_utc_time:
                        
                        unique_id = str(uuid.uuid4())
                        game_data["date"] = date_obj.strftime("%B %d, %Y at %I:%M %p")
                        game_data["opponent"] = game_information[0]
                        sport_link = x.replace("https://godrakebulldogs.com/sports/", "").replace("/schedule", "")
                        
                        if sport_link == "softball":
                            game_data["sport"] = "Softball"

                        elif sport_link == "mens-tennis":
                            game_data["sport"] = "Mens Tennis"

                        elif sport_link == "mens_soccer":
                            game_data["sport"] = "Mens Soccer"

                        elif sport_link == "womens-soccer":
                            game_data["sport"] = "Womens Soccer"

                        elif sport_link == "womens-tennis":
                            game_data["sport"] = "Womens Tennis"
                        
                        game_data["id"] = unique_id
                        
                        
                        if game_data["date"] in all_games.keys():
                            all_games[game_data["date"]][unique_id] = game_data
                        
                        else:
                            all_games[game_data["date"]] = {unique_id : game_data}
                        

        return json.dumps(all_games)

    def link_organizer(self, game_dict):
        if game_dict["sport"] == "Softball":
            schedule_link = "https://godrakebulldogs.com/sports/softball/schedule"

        elif game_dict["sport"] == "Mens Tennis":
            schedule_link = "https://godrakebulldogs.com/sports/mens-tennis/schedule"

        elif game_dict["sport"] == "Mens Soccer":
            schedule_link = "https://godrakebulldogs.com/sports/mens-soccer/schedule"

        elif game_dict["sport"] == "Womens Soccer":
            schedule_link = "https://godrakebulldogs.com/sports/womens-soccer/schedule"

        elif game_dict["sport"] == "Womens Tennis":
            schedule_link = "https://godrakebulldogs.com/sports/womens-tennis/schedule"

        return schedule_link

    def update_score(self, game_dict):
        
        schedule_link = self.link_organizer(game_dict)

        info, info2, _ = self.scrape(schedule_link)

        for i in range(len(info)):
            
            if info[i].find("a") != None:
                game_information = info[i].find("a")['aria-label'].split(" on ", 1)
                
                date_obj, current_utc_time = self.date_converter(game_information)

                game_date = datetime.strptime(game_dict["date"], "%B %d, %Y at %I:%M %p")

                if date_obj == game_date and game_information[0] == game_dict["opponent"]:
                    
                    if i < len(info2):
                        span = info2[i].find_all("span")

                        if len(span) > 3:
                            if span[1].get_text().replace(",", "") == "W":
                                game_dict["winner"] = True
                            elif span[1].get_text().replace(",", "") == "L":
                                game_dict["winner"] = False

                            game_dict["score"] = span[2].get_text()
                        else:
                            game_dict["winner"] = None
                            game_dict["score"] = None

                    else:
                        game_dict["winner"] = None
                        game_dict["score"] = None
                    
                    break

        return game_dict


    def game_today(self):
        today_list = []
        game_data = json.loads(self.upcoming_schedule())

        current_utc_time = str(datetime.now(timezone.utc))
        current_utc_time = datetime.fromisoformat(current_utc_time).replace(tzinfo=None)

        check_date = ""
        check_date = "2025-05-07T00:00:00"
        for i in game_data.keys():
            date_long = datetime.strptime(i, "%B %d, %Y at %I:%M %p")
            date = date_long.date()

            if date == current_utc_time.date():
                check_date = date_long
        
        if check_date != "":
            return list(game_data[check_date].values())
    
        return today_list
    
    def betting(self, game_dict):
        today_game_betting = []

        for y in game_dict:
            schedule_link = self.link_organizer(y)

            info, info2, history_links = self.scrape(schedule_link)
            
            drake_total = 0
            game_counter = 0

            for i in info2:

                span = i.find_all("span")
                if len(span) > 2:
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
                    
                    date_obj, current_utc_time = self.date_converter(game_information)

                    game_date = datetime.strptime(y["date"], "%B %d, %Y at %I:%M %p")

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

                        ml = self.mLineGenerator(game_data)
                        spread = self.spreadGenerator(game_data)
                        overUnder = self.overUnderGenerator(game_data)

                        y["betting"] = {
                            "ml" : ml,
                            "spread" : spread["spread"],
                            "overUnder" : overUnder["over_under"]
                        }

                        today_game_betting.append(y)

                        return today_game_betting

    def mLineGenerator(self, game_data):
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

    def spreadGenerator(self, game_data):
        home_avg_spread = abs(game_data['home_data']['PPG'])
        away_avg_spread = abs(game_data['away_data']['PPG'])
        combined_average_spread = (home_avg_spread + away_avg_spread) / 2
        return {'spread': round(combined_average_spread)}

    def overUnderGenerator(self, game_data):
        return {'over_under': round(game_data['home_data']['PPG'] + game_data['away_data']['PPG'])}


#print(upcoming_schedule())

"""new_dict = [{'date': 'March 29, 2025 at 11:00 AM', 'opponent': 'Indiana State', 'sport': 'Softball', 'id' : "121"}]
#print(update_score(new_dict))
#print(upcoming_schedule())
#print(game_today())
#print(betting(new_dict))

wp = WebScraper()
print(wp.betting(new_dict))"""
