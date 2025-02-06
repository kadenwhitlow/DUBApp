import boto3

class DynamoTable:
    
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name):
        
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.table_name = table_name
        
    def getItemFromTable(self, key_value):
                
        dynamodb = boto3.client(
            "dynamodb",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

        key = {
            "user_id": {"S": f'{key_value}'}
        }

        try:
            response = dynamodb.get_item(TableName=self.table_name, Key=key)
            
            item = response.get("Item")
            
            if item:
                print("Retrieved item:")
                print(item)
            else:
                print("Item not found.")

        except dynamodb.exceptions.ResourceNotFoundException:
            print(f"Table '{self.table_name}' not found.")
            
