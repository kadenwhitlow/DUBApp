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
        
    def returnAllTableItems(self):
        response = self.table.scan()
        return response.get("Items", [])
        
    def getItemFromTable(self, key_value):

        key = {
            "user_id": {"S": f'{key_value}'}
        }

        try:
            response = self.dynamodb.get_item(TableName=self.table_name, Key=key)
            
            item = response.get("Item")
            
            if item:
                print("Retrieved item:")
                print(item)
            else:
                print("Item not found.")

        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"Table '{self.table_name}' not found.")
            
