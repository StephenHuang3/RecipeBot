import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("bakingrecipes4")


def update_scanned_items():
    last_evaluated_key = None

    while True:
        # Scan the table for items with "scanned" set to True, with pagination
        if last_evaluated_key:
            response = table.scan(
                FilterExpression="scanned = :scanned",
                ExpressionAttributeValues={":scanned": True},
                ExclusiveStartKey=last_evaluated_key,
            )
        else:
            response = table.scan(
                FilterExpression="scanned = :scanned",
                ExpressionAttributeValues={":scanned": True},
            )

        # Iterate through the items and update their "scanned" attribute to False
        for item in response["Items"]:
            table.update_item(
                Key={"Id": item["Id"]},
                UpdateExpression="SET scanned = :new_scanned",
                ExpressionAttributeValues={":new_scanned": False},
            )
            print(f"Updated item with ID {item['Id']} - scanned set to False")

        # Check if there are more items to process
        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]
        else:
            break


update_scanned_items()
