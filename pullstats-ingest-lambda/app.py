# pullstats-ingest-lambda.py - MLB API ingest app
# N. Schatz - 10/12/22
# Version 1

# Required Modules:
#
# - requests
# - boto3
 
# Required Lambda Layers:
#
# - AWS SAM CLI package (used for deployment)

# Changelog:
#
# 10/12/22 - Initial script

# To do:
#
#  - Implement SQS resource, tie into app/SAM
#  - Generate ingest logic

# imports
import json
import boto3
import boto3.session
from botocore.config import Config
import warnings
import logging
import datetime
import requests
from requests.exceptions import HTTPError

# establish logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    # set option that silences "futurewarning" (see: https://github.com/boto/botocore/issues/2705)
    warnings.filterwarnings('ignore', category=FutureWarning, module='botocore.client')

    # establish sqs client
    boto_sqs = boto3.client('sqs', endpoint_url='https://sqs.us-east-1.amazonaws.com')

    # get sqs queue details
    sqs_queue_details = boto_sqs.list_queues(
        QueueNamePrefix = "pullstats",
        MaxResults = 1
    )

    # separate out sqs queue url
    sqs_queue_url = sqs_queue_details['QueueUrls'][0]

    # pull game date/key index
    index_years = [2020, 2021, 2022]
    for year in  index_years:
        url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&gameTypes=R,F,D,L,W,C,P&season=' + str(year) + '&fields=dates,games,gamePk,gameDate'
        try:
            index_req = requests.get(url)
            index_req.raise_for_status()
        except HTTPError as http_err:
            print(f'Game Index API call returned HTTP error')
        except Exception as err:
            print(f'Game Index API call returned a non-HTTP error')
        else:
            print(f'Game Index API call successful')
    
        print(f'entering type conversion')

        # conv request object to JSON text
        index_req_text = index_req.text

        print(f'exiting conversion')

        # send index data to SQS
        sqs_response = boto_sqs.send_message(
            QueueUrl = sqs_queue_url,
            MessageBody = index_req_text,
            MessageGroupId = 'pullstats'
        )

        print (f'exiting queue send for year {year}')

    # # get requested import dates from lambda call
    # start_date_string = event.get('start_date')
    # end_date_string = event.get('end_date')

    # # convert from string to datetime
    # date_format = "%m/%d/%Y"
    # start_date = datetime.datetime.strptime(start_date_string, date_format)
    # end_date = datetime.datetime.strptime(end_date_string, date_format)

    # # check for date sanity vs available dataset
    # if start_date.year > 2019 and end_date.year < 2023:
    #     # make API request
    #     for url in ['https://statsapi.mlb.com/api/v1/people?personIds=605151,592450&season=2018&hydrate=education']:
    #         try:
    #             req = requests.get(url)
    #             req.raise_for_status()
    #         except HTTPError as http_err:
    #             print(f'Game Data API call returned HTTP error')
    #         except Exception as err:
    #             print(f'Game Data API call returned a non-HTTP error')
    #         else:
    #             print(f'Game Data API call successful')
    # else:
    #     logger.error(f'start year {start_date.year} or end year {end_date.year} is not a valid year.')

    # # conv API response to text
    # req_text = req.text

    # # sqs test
    # response = boto_sqs.send_message(
    #     QueueUrl = sqs_queue_url,
    #     MessageBody = req_text,
    #     MessageGroupId = 'pullstats'
    # )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "HTTP 200",
        }),
    }