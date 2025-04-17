import random
import string
import time
from threading import Thread
from datetime import datetime
import schedule
from DUBDatabaseFiles.DynamoDBClass import DynamoTable, RedemptionCodeTable

class GeneratePoints:
    def __init__(self):
        self.code_table = DynamoTable("DUBRedemptionCodes")
        self.user_table = DynamoTable("DUBUsers")

        thread = Thread(target=self._schedule_thread, daemon=True)
        thread.start()
        self.refresh_codes()  

        schedule.every().sunday.at("00:00").do(self.refresh_codes) # weekly refresh

    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def refresh_codes(self):
        self.code_table.clearTable()
        point_values = [50, 40, 30, 20, 10]
        for value in point_values:
            for _ in range(2): 
                code = self.generate_code()
                self.code_table.addItem({
                    'code': code,
                    'points': value,
                    'used': False,
                    'created_at': datetime.now().isoformat()
                })

    def redeem_code(self, username, code):
        code_entry = self.code_table.getItem("code", code)
        if not code_entry or code_entry.get('used'):
            return {"error": "Invalid code"}, 400

        user = self.user_table.getItem("user_id", username)
        if not user:
            return {"error": "User not found."}, 404

        new_balance = user["account_balance"] + code_entry["points"]
        self.user_table.updateItem("user_id", username, "account_balance", new_balance)
        self.code_table.updateItem("code", code, "used", True)

        return {"message": "Code redeemed successfully", "new_balance": new_balance}, 200

    def _schedule_thread(self):
        while True:
            schedule.run_pending()
            time.sleep(60)
