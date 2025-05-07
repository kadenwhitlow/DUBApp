import boto3
import logging
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

#export AWS_ACCESS_KEY_ID=""
#export AWS_SECRET_ACCESS_KEY=""
#export AWS_DEFAULT_REGION="us-east-1"

class DynamoTable:
    
    
    def __init__(self, table_name):
        
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = self.dynamodb.Table(self.table_name)
        
    from decimal import Decimal

    def convert_floats_to_decimal(self, obj):
        if isinstance(obj, list):
            return [self.convert_floats_to_decimal(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))  # Use str to avoid floating point issues
        else:
            return obj


    def updateBetStatus(self, user_id, bet, user_balance):
        self.removeBetFromTable(bet, user_id)
        self.addBetToCompletedTable(bet, user_id)

        # Ensure win_amount is a Decimal before adding
        win_amount = bet['verified_results'].get('win_amount', 0)
        if isinstance(win_amount, float):
            win_amount = Decimal(str(win_amount))
        elif isinstance(win_amount, int):
            win_amount = Decimal(win_amount)

        # Ensure user_balance is a Decimal too
        if isinstance(user_balance, float):
            user_balance = Decimal(str(user_balance))
        elif isinstance(user_balance, int):
            user_balance = Decimal(user_balance)

        self.addBalanceToTable(user_balance, user_id, win_amount)

        
    def removeBetFromTable(self, bet_to_remove, user_id):
        try:
            # Get current bets
            response = self.table.get_item(Key={'user_id': user_id})
            current_bets = response.get('Item', {}).get('current_bets', [])

            if bet_to_remove in current_bets:
                current_bets.remove(bet_to_remove)

                # Update the table with the new list
                self.table.update_item(
                    Key={'user_id': user_id},
                    UpdateExpression="SET current_bets = :updated_bets",
                    ExpressionAttributeValues={':updated_bets': current_bets},
                    ReturnValues="UPDATED_NEW"
                )
        except ClientError as err:
            logger.error(
                "Couldn't remove bet for player %s in table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        
        
    def addBetToCompletedTable(self, bet, user_id):
        try:
            bet = self.convert_floats_to_decimal(bet)  # 🔥 Fix is here

            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET previous_bets = list_append(if_not_exists(previous_bets, :empty_list), :new_bet)",
                ExpressionAttributeValues={
                    ':new_bet': [bet],
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as err:
            logger.error(
                "Couldn't add bet to completed for player %s in table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise


    
    def addBetToTable(self, bet_list, user_id):
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET current_bets = list_append(if_not_exists(current_bets, :empty_list), :new_bet)",
                ExpressionAttributeValues={
                    ':new_bet': [bet_list],
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as err:
            logger.error(
                "Couldn't update bet for player %s in table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    
    def subtractBalanceFromTable(self, current_balance, user_id, bet_value):
        new_balance = Decimal(current_balance) - Decimal(bet_value)

        response = self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="SET account_balance = :new_balance",
            ExpressionAttributeValues={':new_balance': new_balance},
            ReturnValues="UPDATED_NEW"
        )
        
        return response
    
    def addBalanceToTable(self, current_balance, user_id, bet_winnings):
        new_balance = Decimal(current_balance) + Decimal(bet_winnings)

        response = self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="SET account_balance = :new_balance",
            ExpressionAttributeValues={':new_balance': new_balance},
            ReturnValues="UPDATED_NEW"
        )
        
        return response

        
    def addUserToTable(self, username, password, email, date):
        try:
            self.table.put_item(
                Item={
                    "user_id": username,
                    "password": password,
                    "email": email,
                    'total_losses': 0, 
                    'current_bets': [], 
                    'account_balance': 0, 
                    'date_joined': date, 
                    'previous_bets': 0, 
                    'total_winnings': 0
                }
            )
        except ClientError as err:
            logger.error(
                "Couldn't add user %s to table %s. Here's why: %s: %s",
                username,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
        
        
        
    def addCodesToTable(self, code_data, user_id):
        code_str = code_data['code']  # Extract the actual code string
        try:
            self.table.update_item(
                Key={'feature_id': user_id},
                UpdateExpression="SET codes.#c = :code_val",
                ExpressionAttributeNames={"#c": code_str},
                ExpressionAttributeValues={":code_val": code_data},
            )
            print(f"Successfully added code: {code_str}")
        except ClientError as e:
            print(f"Couldn't add code {code_str}: {e}")



    def get_code_details(self, code):
        # Read the item with feature_id = "points_codes"
        item = self.code_table.getItem("feature_id", "points_codes")

        if not item:
            return {"error": "points_codes entry not found."}, 404

        codes_dict = item.get("codes", {})

        # Check if the code exists
        if code in codes_dict:
            return {"code": code, "details": codes_dict[code]}, 200
        else:
            return {"error": "Code not found."}, 404


        
        
        
    def returnAllTableItems(self):
        response = self.table.scan()
        return response.get("Items", [])
        
    def getItemFromTable(self, key_value):
            key = {
                "user_id": key_value  # Corrected key format for DynamoDB
            }


            try:
                # Use self.table.get_item instead of self.dynamodb.get_item
                response = self.table.get_item(Key=key)
                item = response.get("Item")

                if item:
                    print("Retrieved item:")
                    return item
                else:
                    print("Item not found.")

            except ClientError as err:
                if err.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(f"Table '{self.table_name}' not found.")
                else:
                    print(f"An error occurred: {err.response['Error']['Message']}")
            
