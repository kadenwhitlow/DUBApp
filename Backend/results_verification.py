



def bet_checker(results_data, bet_data):
    if results_data['score'] is not None:
          final_result = None
          win_amount = 0
          
          #if bet_data[results_data['game_id']]['type_of_bet'] == "moneyline":
          #      pass
          bet_results = {
              "bet_status": "finished",
              "bet_result": final_result,
              "win_amount": win_amount,
              
              
          }
    else:
          bet_results = {
          "bet_status": "pending",
          "bet_result": None,
          "win_amount": None,
          
          
      }
    return bet_results
    

def verify_results(user_data, game_database, results, date):
    
    bet_ids = []
    bet_dict = {}
    
    for i in user_data['current_bets']:
        try:
            bet_ids.append(i['game_id'])
            bet_dict[i['game_id']] = i
            bet_dict[i['game_id']]["date"] = date
            bet_dict[i['game_id']]["opponent"] = game_database[date][i['game_id']]['opponent']
            bet_dict[i['game_id']]["sport"] = game_database[date][i['game_id']]['sport']
        except:
            pass
        
    print(bet_dict)
    
    #get the id that was stored in the user bet database
    #check the list of games for the day, and match up the id with the one for our bet
    
    #need to verify which game in the results is the one we are looking for
    # check the results to see if the sport and the opponent match up
    # if the sport and opponent match up, then we can check the results
    results_data = {}
    for i in results:
        for m in bet_ids:
            if (i['sport'] == bet_dict[m]['sport']) and (i['opponent'] == bet_dict[m]['opponent']):
                results_data[m] = i
    print(results_data)
    if results_data is {}:
        return "The game is not in the results"
    else:
        for game_id in results_data:
              bet_checker(results_data[game_id], bet_dict)
        
    
    
    

    
dummy_data = {
    "user_data": {
        "account_balance": 100,
        "current_bets": [
            {
            "bet_odds": "-120",
            "bet_prop": "Moneyline",
            "bet_status": "pending",
            "bet_value": 10,
            "player": "Drake",
            "type_of_bet": "moneyline",
            "game_id": "8a0cde7a-991f-4ab9-8398-fb98b5991d03"
            }, 
            {
            "bet_odds": "+3",
            "bet_prop": "Spread",
            "bet_status": "pending",
            "bet_value": 5,
            "player": "Drake",
            "type_of_bet": "spread",
            "game_id": "caabecf3-186b-4d75-bd91-185ed7c2d0ad"
            }
            ],
        "date_joined": "2023-10-01",
        "email": "user@gmail.com",
        "password": "password123",
        "total_losses": 0,
        "total_winnings": 0,
    },
    "game_database": {
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
},
    "results": [
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
    ],
    "date": "2025-04-05T14:00:00"
}
verify_results(dummy_data['user_data'], dummy_data['game_database'], dummy_data['results'], dummy_data['date'])