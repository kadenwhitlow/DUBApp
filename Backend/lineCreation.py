

class LineCreator():
    
    def __init__(self, game_data):
        self.game_data = game_data
        
        #game_data = {
        #    'home_data': {
        #        'Wins': Int,
        #        'Losses': Int,
        #        'PPG': Float,
        #        'OPP_PPG': Float,
        #        'SOS': Float,
        #     },
        #    'away_data': {
        #        'Wins': Int,
        #        'Losses': Int,
        #        'PPG': Float,
        #        'OPP_PPG': Float,
        #        'SOS': Float
        #     },
        #}
        
    #win_perc*SOS
    #0.67*0.357=0.23919  * 100 = 23.919
    #0.90*0.658=(0.5922) * 100 = 59.22
        
    def teamRatingCalculator(self):
        
        
        return None
        
    def mLineGenerator(self):
        
        home_win_perc = self.game_data['home_data']['Wins']/(self.game_data['home_data']['Wins']+self.game_data['home_data']['Losses'])
        home_win_value = (home_win_perc*self.game_data['home_data']['SOS']) * 100
        away_win_perc = self.game_data['away_data']['Wins']/(self.game_data['away_data']['Wins']+self.game_data['away_data']['Losses'])
        away_win_value = (away_win_perc*self.game_data['away_data']['SOS']) * 100
        
        if home_win_perc > away_win_perc:
            
            difference = home_win_value - away_win_value
            away_ml = round((difference-11.37) * 10)
            home_ml = round(difference*10)
            return {'home_ml': f"-{home_ml}", 'away_ml': f"+{away_ml}"}
        
        else:
            
            difference = away_win_value - home_win_value
            home_ml = round((difference-11.37) * 10)
            away_ml = round(difference*10)
            return {'home_ml': f"-{home_ml}", 'away_ml': f"+{away_ml}"}
    
    def spreadGenerator(self):
        
        #check each teams avg diff between PPG and OPP PPG (average spread)
        home_avg_spread = abs(self.game_data['home_data']['PPG'] - self.game_data['home_data']['OPP_PPG'])
        away_avg_spread = abs(self.game_data['away_data']['PPG'] - self.game_data['away_data']['OPP_PPG'])
        combined_average_spread = (home_avg_spread+away_avg_spread)/2
        
        #compare each team PPG
        ppg_diff = abs(self.game_data['home_data']['PPG']-self.game_data['away_data']['PPG'])
        return {'spread': round(combined_average_spread)}
    
    def overUnderGenerator(self):
        
        return None
    
    
gd = {
    'home_data': {
        'Wins': 9,
        'Losses': 1,
        'PPG': 67.5,
        'OPP_PPG': 55.9,
        'SOS': 0.658,
     },
    'away_data': {
        'Wins': 6,
        'Losses': 3,
        'PPG': 76.3,
        'OPP_PPG': 71.1,
        'SOS': 0.357
     },
}
LC = LineCreator(gd)

print(LC.mLineGenerator())
print(LC.spreadGenerator())