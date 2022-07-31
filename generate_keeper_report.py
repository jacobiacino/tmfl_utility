from tmfl_utility.league import League
from tmfl_utility.players import Players
import pandas as pd
import os
import awswrangler as wr
import boto3

# This file was a quick check written to evaluate how keeper rules should work for the
# TMFL in 2022. The investigation was centered around which FA pickups from the 2021
# season performed the best, and if it would make sense to allow FA pickups to be
# kept. 

# Read league ID from environment variable [so it's not publicly exposed ;)]
league_id = os.environ['LEAGUE_ID']
l = League(league_id)
keepers = l.get_keeper_report()

P = Players()
player_list = P.get_players()

keeper_info = [
    {
        'id': a.get("id"),
        'rights_holder': a.get("rights_holder"),
        'round_selected': a.get("round_selected"),
        'keeper_eligible': a.get('keeper_eligible'),
        'keeper_cost': a.get('keeper_cost'),
        'name': player_list[a.get("id")].get('search_full_name', a.get('id')),
        'positions': player_list[a.get("id")].get('fantasy_positions')
    }
    for a in keepers
]

k = pd.DataFrame(keeper_info)

s3_target = os.environ["s3_target"]
s3_location = "s3://{}/07-31-2022/00:00:59/adp_data.csv".format(s3_target)

adps = wr.s3.read_csv(path=s3_location)

def adp_to_round(row):
    return (int(row['avg_adp'] / 12)) + 1

def keeper_value(row):
    return row['keeper_cost'] - row['round_adp'] if row['keeper_eligible'] else None

adps['round_adp'] = adps.apply(lambda row: adp_to_round(row), axis=1)

merged = pd.merge(left=k, right=adps, left_on='name', right_on='name')

merged['value'] = merged.apply(lambda row: keeper_value(row), axis=1)

merged = merged.sort_values(by='value', ascending=False)

filtered = merged.loc[merged['keeper_eligible']]

wr.s3.to_csv(
    filtered,
    path=s3_location
)
