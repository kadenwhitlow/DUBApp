from collections import Counter

class TopBets:
    def __init__(self, dynamo_table):
        self.dynamo_table = dynamo_table

    def get_top_bets(self, top_n=3):
        all_users = self.dynamo_table.returnAllTableItems()
        bet_type_counts = Counter()

        for user in all_users:
            for parlay in user.get("current_bets", []):
                for bet in parlay:
                    bet_type = bet.get("type_of_bet")
                    if bet_type:
                        bet_type_counts[bet_type.strip()] += 1

        return dict(bet_type_counts.most_common(top_n))
