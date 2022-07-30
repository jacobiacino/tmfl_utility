from tmfl_utility.league import League
import pandas as pd
import os

# This file was a quick check written to evaluate how keeper rules should work for the
# TMFL in 2022. The investigation was centered around which FA pickups from the 2021
# season performed the best, and if it would make sense to allow FA pickups to be
# kept. 

# Read league ID from environment variable [so it's not publicly exposed ;)]
league_id = os.environ['LEAGUE_ID']
l = League(league_id)
all_adds = l.get_completed_waiver_or_fa_adds()

transactions = pd.DataFrame(all_adds)

# ADP data sourced from https://www.fantasypros.com/nfl/adp/half-point-ppr-overall.php
adps = pd.read_csv('./data/adp.csv')[['player', 'sleeper', 'avg']]
# Sleeper removes name suffixes
adps['player'] = adps['player'].str.replace('II', '')
adps['player'] = adps['player'].str.replace('III', '')
adps['player'] = adps['player'].str.replace('Jr.', '')
# Sleeper puts all names lowecase
adps['player'] = adps['player'].str.lower()
# Sleeper removes all periods
adps['player'] = adps['player'].str.replace('.', '')
# Sleeper removes all spaces
adps['player'] = adps['player'].str.replace(' ', '')


# Stats aren't really useful here, as the value of a keeper is mostly determined
# by current-year ADP, but they are an interesting inclusion
# Stats from 2021 season, not half PPR, but provide directional analysis
# sourced from https://www.pro-football-reference.com/years/2021/fantasy.htm
player_stats = pd.read_csv('./data/stats.csv')[['Player', 'PPR', 'Rk']]
# PFR uses these indicators for accolades, remove them
player_stats['Player'] = player_stats['Player'].str.replace('*', '')
player_stats['Player'] = player_stats['Player'].str.replace('+', '')
# Sleeper removes name suffixes
player_stats['Player'] = player_stats['Player'].str.replace('II', '')
player_stats['Player'] = player_stats['Player'].str.replace('III', '')
player_stats['Player'] = player_stats['Player'].str.replace('Jr.', '')
# Sleeper puts all names lowecase
player_stats['Player'] = player_stats['Player'].str.lower()
# Sleeper removes all periods
player_stats['Player'] = player_stats['Player'].str.replace('.', '')
# Sleeper removes all spaces
player_stats['Player'] = player_stats['Player'].str.replace(' ', '')

merged_up = pd.merge(left=transactions, right=player_stats, left_on='name', right_on='Player')
adps = pd.merge(left=merged_up, right=adps, left_on='Player', right_on='player')
adps = adps.sort_values(by='avg', ascending=True)

adps.to_csv('ranked_fa_adds.csv')

