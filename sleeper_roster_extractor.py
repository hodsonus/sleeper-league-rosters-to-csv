import json
import os
import pandas as pd
from requests import get


base_url = 'https://api.sleeper.app/v1/'
league_id = '000000000000000000'
league_url = base_url + 'league/' + str(league_id) + '/'


def main():

    rosters = get(league_url + 'rosters').json()
    ownerid_to_playerids = get_ownerid_to_playerids(rosters)

    owners = get(league_url + 'users').json()
    ownerid_to_ownerdisplaynames = get_ownerid_to_ownerdisplaynames(owners)

    players = get(base_url + 'players/nfl').json()

    ownerdisplayname_to_playerattributelists, playerattributelist_columns = resolve_ids_to_names_and_attributelists(ownerid_to_playerids, ownerid_to_ownerdisplaynames, players)
        
    os.makedirs("./rosters/", exist_ok=True)

    for ownerdisplayname in ownerdisplayname_to_playerattributelists:
        roster_df = pd.DataFrame(ownerdisplayname_to_playerattributelists[ownerdisplayname], columns = playerattributelist_columns)
        file_name = './rosters/' + str(ownerdisplayname) + ".csv"
        roster_df.to_csv(file_name, encoding='utf-8', index=False)


def get_ownerid_to_ownerdisplaynames(owners):
    ownerid_to_ownerdisplaynames = {}
    for owner in owners:
        ownerid_to_ownerdisplaynames[owner["user_id"]] = owner["display_name"]
    return ownerid_to_ownerdisplaynames


def resolve_ids_to_names_and_attributelists(ownerid_to_playerids, ownerid_to_ownerdisplaynames, players):
    ownerdisplayname_to_playerattributelists = {}

    for ownerid in ownerid_to_playerids:

        ownerdisplayname = ownerid_to_ownerdisplaynames[ownerid]
        ownerdisplayname_to_playerattributelists[ownerdisplayname] = []

        for player_id in ownerid_to_playerids[ownerid]:

            player = players[player_id]

            full_name = player["full_name"]
            age = player["age"]
            years_exp = player["years_exp"]
            height = player["height"]
            weight = player["weight"]
            college = player["college"]
            fantasy_positions = ",".join(player["fantasy_positions"])

            ownerdisplayname_to_playerattributelists[ownerdisplayname] += [[full_name, age, years_exp, fantasy_positions, height, weight, college]]
    
    playerattributelist_columns = ['Name', 'Age', "YoE", "Eligibility", "Height", "Weight", "College"]
    return ownerdisplayname_to_playerattributelists, playerattributelist_columns


def get_ownerid_to_playerids(rosters):
    ownerid_to_playerids = {}
    for roster in rosters:

        owner_id = roster["owner_id"]
        ownerid_to_playerids[owner_id] = []
    
        for taxi_playerid in roster["taxi"]:
            if not is_int(taxi_playerid):
                continue
            ownerid_to_playerids[owner_id] += [taxi_playerid]

        for starter_playerid in roster["starters"]:
            if not is_int(starter_playerid):
                continue
            ownerid_to_playerids[owner_id] += [starter_playerid]

        for bench_playerid in roster["players"]:
            if not is_int(bench_playerid):
                continue
            ownerid_to_playerids[owner_id] += [bench_playerid]

    return ownerid_to_playerids


def is_int(s):
    try: 
        int(s)
        return True
    except ValueError: 
        return False


if __name__ == "__main__":
    main()