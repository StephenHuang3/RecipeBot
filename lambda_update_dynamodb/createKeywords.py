import boto3
import logging
import time
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

dynamodb = boto3.resource("dynamodb")
source_table = dynamodb.Table("bakingrecipes4")
target_table = dynamodb.Table("bakingrecipes4_keywordsv2")


def copy_and_split_items():
    last_evaluated_key = None
    processed_items = 0

    while True:
        # Scan the source DynamoDB table with pagination
        if last_evaluated_key:
            response = source_table.scan(ExclusiveStartKey=last_evaluated_key)
        else:
            response = source_table.scan()

        items = response["Items"]

        # Iterate through the items and split the title into keywords
        for item in items:
            # Check if the item already has keywords
            if item["scanned"] == False:
                title = item["title"]
                keywords = re.split(r"[\s()-]", title.lower())

                # Create new items in the target table with separate keywords
                for uncleanedkeyword in keywords:
                    pattern = re.compile(
                        r"^[\d&\-!#\\:,\(\)\*/?\"]*|[\d&\-!#\\:,\(\)\*/?\"]*$"
                    )
                    keyword = pattern.sub("", uncleanedkeyword)
                    if (
                        keyword == ""
                        or keyword == "and"
                        or keyword == "or"
                        or keyword == "the"
                        or keyword == "a"
                        or keyword == "in"
                    ):
                        continue

                    new_item = item.copy()
                    new_item["Id"] = f"{new_item['Id']}_{keyword}"
                    new_item["keywords"] = keyword
                    logger.info(
                        f"Creating new item with ID {new_item['Id']} - keyword: {keyword}"
                    )

                    # Insert the new record into the target table
                    target_table.put_item(Item=new_item)
                    source_table.update_item(
                        Key={"Id": item["Id"]},
                        UpdateExpression="SET scanned = :scanned",
                        ExpressionAttributeValues={":scanned": True},
                    )

                    processed_items += 1
            else:
                logger.info(
                    f"Skipping item with ID {item['Id']} - keywords already exist"
                )

        # Check if there are more items to process
        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]
        else:
            break

    logger.info(f"Processed a total of {processed_items} items")
    return {"message": "Items copied and split successfully"}


def lambda_handler(event, context):
    return copy_and_split_items()


lambda_handler(None, None)
