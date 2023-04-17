This folder contains information on how I updated my dynamodb collection so I can query for word in the title of each item.
before, the title may contain many words and I cannot query for a flavor and item at the same time without there having a change of missing something

steps:

1. create a lambda function with python runtime

2. update the IAM role with the following JSON

{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": [
"dynamodb:Scan",
"dynamodb:UpdateItem"
],
"Resource": "arn:aws:dynamodb:YourRegion:YourAWSAccountID:table/YourTableName"
}
]
}

this should give read and write permissions to your dynamodb table. replace the information in "Resource" with your own region, accoundID, table name.

3. create a virtual environment with the following commands

for Windows:
python -m venv venv

.\venv\Scripts\activate

pip install boto3

deactivate

for macOS/linux:
python3 -m venv venv

source venv/bin/activate

pip install boto3

deactivate

4. Create the deployment package by compressing the contents of the venv/Lib/site-packages folder (for Windows) or venv/lib/python3.x/site-packages folder (for macOS/Linux) along with the py script files. Make sure to compress the contents directly, not the folder itself.

5. upload the zip file to your lambda function

6. change the laambda handler to <file you are running>.lambda_handler

7. run the scripts importcsv.py, createKeywords.py. you can start and stop createKeywords.py at any time. if there was an issue, run restartScan.py

8. your database is now properly configured
