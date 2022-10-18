# pullstats-ingest-lambda.py - MLB API ingest app
# N. Schatz - 10/17/22
# Version 2

# Required Modules:
#
# - requests
# - boto3
# - pg8000
 
# Required Deployment Tools:
#
# - AWS SAM CLI package (used for deployment)

# Changelog:
#
# 10/12/22 - Initial script
# 10/17/22 - Added logic for game json queue population
# 10/18/22 - Comments/finalization

# To do:
#
#  - move secrets to AWS Secrets Manager calls

# imports
import json
import boto3
import boto3.session
from botocore.config import Config
import pg8000.native
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

    # establish postgres db connection
    postgres_conn = pg8000.native.Connection(
        user="pullstatsadmin",
        password="ChangeMe!",
        host="<your_hostname>",
        port="5432",
        database="PullStats"
    )

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
    
        # conv request object to JSON text
        index_req_text = index_req.text

        # send index data to SQS
        sqs_response = boto_sqs.send_message(
            QueueUrl = sqs_queue_url,
            MessageBody = index_req_text,
            MessageGroupId = 'pullstats'
        )

        print (f'exiting queue send for index year {year}')

    # get requested import dates from lambda call
    start_date_string = event.get('start_date')
    end_date_string = event.get('end_date')

    # convert from string to datetime
    date_format = "%m/%d/%Y"
    start_date = datetime.datetime.strptime(start_date_string, date_format)
    end_date = datetime.datetime.strptime(end_date_string, date_format)

    # check for date sanity vs available dataset
    if start_date.year > 2019 and end_date.year < 2023:
        target_list = []

        # pull set of game ids to retrieve
        try: 
            for row in postgres_conn.run(f"SELECT gamepk FROM gameindex WHERE gamedate BETWEEN '{start_date.date()}' AND '{end_date.date()}';"):
                target_list.append(row[0])
        except Exception as e:
            print(e)
        
        print(f'pulled {len(target_list)} keys')

        # make API requests for games in selected range
        for gamekey in target_list:
            try:
                game_url = 'https://statsapi.mlb.com/api/v1.1/game/' + str(gamekey) + '/feed/live?fields=gameData,game,pk,type,datetime,officialDate,teams,away,id,name,home,id,name,players,id,firstName,lastName,active,isPlayer,currentAge,weight,height,birthCountry,draftYear,primaryPosition,name,batSide,code,pitchHand,code,venue,id,name,weather,condition,temp,wind,liveData,plays,allPlays,result,event,description,matchup,batter,id,fullName,batSide,code,pitcher,id,fullName,pitchHand,code'
                game_req = requests.get(game_url)
                game_req.raise_for_status()

                # conv request object to JSON text
                game_req_text = game_req.text

                # send json to sqs for processing
                sqs_response = boto_sqs.send_message(
                    QueueUrl = sqs_queue_url,
                    MessageBody = game_req_text,
                    MessageGroupId = 'pullstats',
                    MessageAttributes = {
                        'gamePk': {
                            'StringValue': f'{str(gamekey)}',
                            'DataType': 'String'
                        }
                    }
                    )
                print(f'Game data sent to queue')
            except HTTPError as http_err:
                print(f'Game Data API call returned HTTP error')
            except Exception as err:
                print(f'Game Data API call returned a non-HTTP error')
            else:
                print(f'Game Data API call successful')
    else:
        logger.error(f'start year {start_date.year} or end year {end_date.year} is not a valid year.')

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "HTTP 200",
        }),
    }