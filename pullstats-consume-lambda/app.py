# pullstats-consume-lambda.py - MLB API SQS consume app
# N. Schatz - 10/18/22
# Version 2

# Required Modules:
#
# - requests
# - boto3
# - pg8000
 
# Required Lambda Layers:
#
# - AWS SAM CLI package (used for deployment)

# Changelog:
#
# 10/14/22 - Initial script
# 10/18/22 - Comments/finalization

# To do:
#
#  - Generate SQS queue consumption logic
#  - Better password logic with secrets manager
#  - Correct json parse/import

# imports
import json
import boto3
import boto3.session
from botocore.config import Config
import pg8000.native
import warnings
import requests
from requests.exceptions import HTTPError


def lambda_handler(event, context):

    # set option that silences "futurewarning" (see: https://github.com/boto/botocore/issues/2705)
    warnings.filterwarnings('ignore', category=FutureWarning, module='botocore.client')

    # establish postgresql client
    postgres_conn = pg8000.native.Connection(
        user="pullstatsadmin",
        password="ChangeMe!",
        host="pullstats-aurora-db.cqealbrbwgme.us-east-1.rds.amazonaws.com",
        port="5432",
        database="PullStats"
    )

    # process SQS entry
    for record in event['Records']:
        payload = record["body"].replace("'", "\"")

        # check for record type, process accordingly
        attribs = record["messageAttributes"]

        if attribs:
            try: 
                print(f'json parse for import')
                # payload_string = str(payload)
                # postgres_conn.run(f"INSERT INTO jsonqueue(gameJson) VALUES({payload_string});")
            except Exception as e:
                print(e)
        else:
            # convert JSON to dict
            payload_json = json.loads(payload)

            # generate games key JSON and attempt to upsert records:
            for date in payload_json["dates"]:
                for game in date["games"]:
                    try: 
                        gamePk = game["gamePk"]
                        gameDateTime = game["gameDate"]
                        day, split, time = gameDateTime.partition('T')
                        gameDate = day
                        postgres_conn.run(f"INSERT INTO gameindex(gamepk,gamedate) VALUES({gamePk}, '{gameDate}') ON CONFLICT ON CONSTRAINT gameindex_pkey DO NOTHING;")
                    except Exception as e:
                        print(e)

    # clean up pg connection
    postgres_conn.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "HTTP 200",
        }),
    }