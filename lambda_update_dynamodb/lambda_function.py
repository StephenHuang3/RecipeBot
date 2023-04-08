import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("bakingrecipes")


def update_item(item):
    title = item["title"]
    keywords = title.lower().split()

    response = table.update_item(
        Key={"Id": item["Id"]},
        UpdateExpression="SET keywords = :keywords",
        ExpressionAttributeValues={":keywords": keywords},
    )
    return response


# Scan the table to get all items
response = table.scan()
items = response["Items"]

# Update each item with the new 'keywords' attribute
for item in items:
    update_item(item)
