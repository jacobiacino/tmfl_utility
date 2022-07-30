import json
import requests
import re
import pandas as pd
import boto3
from io import StringIO
from bs4 import BeautifulSoup
import os


def lambda_handler(event, context):
    url = 'https://www.fantasypros.com/nfl/adp/half-point-ppr-overall.php'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    players = soup.select('tbody tr')
    
    team_abbreviations = [
        'ARI',
        'ATL',
        'BAL',
        'BUF',
        'CAR',
        'CHI',
        'CIN',
        'CLE',
        'DAL',
        'DEN',
        'DET',
        'GB',
        'HOU',
        'IND',
        'JAC',
        'KC',
        'LV',
        'LAC',
        'LAR',
        'MIA',
        'MIN',
        'NE',
        'NO',
        'NYG',
        'NYJ',
        'PHI',
        'PIT',
        'SF',
        'SEA',
        'TB',
        'TEN',
        'WAS'
    ]
    
    data = []
    for p in players:
        if (p.select_one(".player-label")) is not None:
            player_name = p.select_one(".player-label").text.strip()
            for t in team_abbreviations:
                if t in player_name:
                    player_name = player_name.replace(t, '')
                    break
    
            player_name = re.sub('\(([^\)]+)\)', '', player_name)
            player_name = player_name.replace('II', '') \
            .replace('III', '') \
            .replace('Jr.', '') \
            .lower() \
            .replace('.', '') \
            .replace('\'', '') \
            .replace('-', '') \
            .replace(' ', '')
    
            elems = p.select("td")
            player_data = {
                'name': player_name,
                'position_rank': elems[2].text.strip(),
                'yahoo_adp': elems[3].text.strip(),
                'fantrax_adp': elems[4].text.strip(),
                'ffc_adp': elems[5].text.strip(),
                'sleeper_adp': elems[6].text.strip(),
                'avg_adp': elems[7].text.strip(),
            }
            data.append(player_data)

    k = pd.DataFrame(data)
    # k.to_csv("./adp_data.csv", index=False)
    
    s3_client = boto3.resource('s3')
    
    csv_buffer = StringIO()
    k.to_csv(csv_buffer, index=False)
    
    s3_target = os.environ['s3_target']
    s3_client.Object(s3_target, 'adp_data.csv').put(Body=csv_buffer.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
