import boto3
import logging
from botocore.exceptions import ClientError
from decimal import Decimal

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
        
    def updateBetStatus(self, user_id, bet):
        self.removeBetFromTable(bet, user_id)
        self.addBetToCompletedTable(bet, user_id)
        
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
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET previous_bets = list_append(if_not_exists(previous_bets, :empty_list), :new_bet)",
                ExpressionAttributeValues={
                    ':new_bet': [bet],  # wrap single bet in a list
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
    
    def addCodesToTable(self, codes, user_id):
        try:
            update_expression = "SET "
            expression_attribute_names = {}
            expression_attribute_values = {}

            for i, code in enumerate(codes):
                code_key = f"#c{i}"
                value_key = f":v{i}"

                update_expression += f"codeMap.{code_key} = {value_key}, "
                expression_attribute_names[code_key] = code
                expression_attribute_values[value_key] = 0

            update_expression = update_expression.rstrip(", ")

            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as err:
            logger.error(
                "Couldn't add codes for user %s in table %s. Here's why: %s: %s",
                user_id,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

        
        
        
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
            
