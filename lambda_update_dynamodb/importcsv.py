import boto3
import csv
import json
import uuid

# Connect to AWS services
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Define constants
bucket_name = "bakingrecipes"
file_name = "RecipeNLG_dataset.csv"
table_name = "bakingrecipes4"
partition_key = "Id"

# Read CSV file from S3 and convert to list of dictionaries
csv_file = (
    s3.get_object(Bucket=bucket_name, Key=file_name)["Body"]
    .read()
    .decode("utf-8")
    .splitlines()
)
csv_reader = csv.DictReader(csv_file)
data = []
for row in csv_reader:
    # Convert lists from strings to Python lists
    list_delimiter = '", "'
    if row["ingredients"] is not None:
        row["ingredients"] = [
            x.strip().strip('"') for x in row["ingredients"].strip("][").split(",")
        ]
    if row["directions"] is not None:
        row["directions"] = [
            x.strip().strip('"') for x in row["directions"].strip("][").split(",")
        ]
    if row["NER"] is not None:
        row["NER"] = [x.strip().strip('"') for x in row["NER"].strip("][").split(",")]

    row["scanned"] = False

    # Add unique Id to each item
    row[partition_key] = str(uuid.uuid4())

    data.append(row)

# Batch-write data to DynamoDB table
table = dynamodb.Table(table_name)
with table.batch_writer() as batch:
    for item in data:
        batch.put_item(Item=item)

# Print success message
print(
    f"Data imported from S3 bucket {bucket_name} file {file_name} to DynamoDB table {table_name} with partition key {partition_key}."
)
