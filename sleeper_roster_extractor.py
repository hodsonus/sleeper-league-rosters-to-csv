import json
from xml.dom import NotFoundErr
import pandas as pd
from requests import get

base_url = 'https://api.sleeper.app/v1/'
league_id = '784488936675385344'
league_url = base_url + 'league/' + str(league_id) + '/'

def add_player_to_roster(rosters_dict, roster_id, player):
    rosters_dict[roster_id] += [player]

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError: 
        return False

def resolve_rosters_dict(players, users, rosters_dict):
    resolved_rosters_dict = {}
    for user_id in rosters_dict:

        user_displayname = None
        for user in users:
            if user["user_id"] == user_id:
                user_displayname = user["display_name"]
                break
        if (user_displayname == None):
            raise NotFoundErr

        resolved_rosters_dict[user_displayname] = []

        for player_id in rosters_dict[user_id]:

            player = players[player_id]
            print(player["full_name"])
            resolved_rosters_dict[user_displayname] += [player]
    
    return resolved_rosters_dict
 
rosters = get(league_url + 'rosters').json()
rosters_dict = {}

for roster in rosters:

    roster_id = roster["owner_id"]
    rosters_dict[roster_id] = []
  
    for taxi_player in roster["taxi"]:
        add_player_to_roster(rosters_dict, roster_id, taxi_player)

    for starter_id in roster["starters"]:
        if not is_int(starter_id):
            continue
        add_player_to_roster(rosters_dict, roster_id, starter_id)

    for player in roster["players"]:
        if not is_int(player):
            continue

        add_player_to_roster(rosters_dict, roster_id, player)

players = get(base_url + 'players/nfl').json()
users = get(league_url + 'users').json()

resolved_rosters_dict = resolve_rosters_dict(players, users, rosters_dict)

roster_lists = {}

for roster_id in resolved_rosters_dict:
    roster_lists[roster_id] = []

    # {
    #     "2103": {
    #       "injury_body_part": null,
    #       "rotoworld_id": null,
    #       "full_name": "Cody Booth",
    #       "metadata": null,
    #       "fantasy_positions": [
    #         "OL"
    #       ],
    #       "sportradar_id": "4cd4976e-e230-4935-ad3f-c12876a41350",
    #       "news_updated": null,
    #       "search_rank": 9999999,
    #       "search_first_name": "cody",
    #       "fantasy_data_id": 16426,
    #       "injury_status": null,
    #       "stats_id": null,
    #       "weight": "285",
    #       "player_id": "2103",
    #       "first_name": "Cody",
    #       "status": "Inactive",
    #       "pandascore_id": null,
    #       "depth_chart_order": null,
    #       "college": "Temple",
    #       "practice_participation": null,
    #       "years_exp": 1,
    #       "position": "OT",
    #       "high_school": null,
    #       "birth_state": null,
    #       "rotowire_id": 9866,
    #       "team": null,
    #       "number": 60,
    #       "espn_id": 17054,
    #       "gsis_id": null,
    #       "birth_city": null,
    #       "birth_date": "1991-04-22",
    #       "yahoo_id": 27841,
    #       "height": "6'5\"",
    #       "last_name": "Booth",
    #       "age": 27,
    #       "swish_id": null,
    #       "depth_chart_position": null,
    #       "injury_notes": null,
    #       "active": false,
    #       "birth_country": null,
    #       "injury_start_date": null,
    #       "practice_description": null,
    #       "sport": "nfl",
    #       "hashtag": "#codybooth-NFL-FA-60",
    #       "search_full_name": "codybooth",
    #       "search_last_name": "booth"
    #     }
    #   }
    for player_object in resolved_rosters_dict[roster_id]:
        full_name = player_object["full_name"]

        age = player_object["age"]
        years_exp = player_object["years_exp"]

        height = player_object["height"]
        weight = player_object["weight"]

        depth = player_object["depth_chart_position"]
        college = player_object["college"]

        fantasy_positions = ",".join(player_object["fantasy_positions"])

        roster_lists[roster_id] += [[full_name, age, years_exp, fantasy_positions, height, weight, depth]]

for roster_id in roster_lists:
    roster_df = pd.DataFrame(roster_lists[roster_id], columns = ['Name', 'Age', "YoE", "Eligibility", "Height", "Weight", "Depth"])
    file_name = str(roster_id) + ".csv"
    roster_df.to_csv(file_name, encoding='utf-8', index=False)