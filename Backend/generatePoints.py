import random
import string
import time
from threading import Thread
from datetime import datetime
import schedule
from DynamoDBClass import DynamoTable

class GeneratePoints:
    def __init__(self):
        self.code_table = DynamoTable("DUBStorage")
        self.user_table = DynamoTable("DUBUsers")

        thread = Thread(target=self._schedule_thread, daemon=True)
        thread.start()
        self.refresh_codes()  

        schedule.every().sunday.at("00:00").do(self.refresh_codes) 

    def generate_code(self, point_value):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        code_data = {
            'code': code,
            'points': point_value,
            'used': False,
            'created_at': datetime.now().isoformat(),
            'category': "points_codes",
            "used_by": []
        }

        self.code_table.addCodesToTable(code_data, "points_codes")
        return code

    def refresh_codes(self):
        self.code_table.clearTable()

        point_values = [50, 40, 30, 20, 10]

        for value in point_values:
            self.generate_code(value)

    def redeem_code(self, username, code):
        code_entry = self.code_table.getItem("code", code)
        if not code_entry or code_entry.get("category") != "points_codes":
            return {"error": "Invalid code."}, 400

        used_by = code_entry.get("used_by", [])
        if username in used_by:
            return {"error": "You’ve already redeemed this code."}, 403

        user = self.user_table.getItem("user_id", username)
        if not user:
            return {"error": "User not found."}, 404

        current_balance = user["account_balance"]
        new_balance = current_balance + code_entry["points"]
        self.user_table.updateItem("user_id", username, "account_balance", new_balance)

        updated_used_by = used_by + [username]
        self.code_table.updateItem("code", code, "used_by", updated_used_by)

        return {
            "message": f"Redeemed {code_entry['points']} points!",
            "new_balance": new_balance
        }, 200

    def _schedule_thread(self):
        while True:
            schedule.run_pending()
            time.sleep(60)
            
