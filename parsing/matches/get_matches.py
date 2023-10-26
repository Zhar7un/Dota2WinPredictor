import requests
import numpy as np
import json
import time


REQUIRED_PLAYER_PROPERTIES_NAMES = ["match_id", "assists", "deaths", "firstblood_claimed", "player_slot",
                                    "gold_per_min", "hero_damage", "hero_healing", "hero_id", "kills", "last_hits",
                                    "net_worth", "stuns", "teamfight_participation", "tower_damage", "xp_per_min",
                                    "duration", "win", "kda", "courier_kills", "roshan_kills", "roshans_killed",
                                    "ancient_kills", "lane_efficiency", "lane_role"]


def get_parsed_matches_ids(less_than_match_id=None):
    url = "https://api.opendota.com/api/parsedMatches/"
    if less_than_match_id is not None:
        url += f"?less_than_match_id={less_than_match_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print("ERROR while fetching matches ids. Response status code:", response.status_code)
        return
    print("Getting matches ids is DONE")
    result = response.json()
    return result


def get_match_by(match_id):
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print("ERROR while fetching match. Response status code:", response.status_code)
        return
    print(f"Getting match is DONE with id {match_id}")
    result = response.json()
    return result


def simplify(*matches):
    result = []
    for match in matches:
        simplified_match = {"radiant_win": match["radiant_win"],
                            "match_id": match["match_id"],
                            "players": []}
        for player in match["players"]:
            player_properties = {property_name: player[property_name]
                                 for property_name in REQUIRED_PLAYER_PROPERTIES_NAMES}

            damage_taken = {"damage_taken": int(np.array([value
                                                          for target, value in player["damage_taken"].items()
                                                          if "hero" in target]).sum())}
            player_properties.update(damage_taken)
            benchmarks_properties = {names: values["raw"] for names, values in player["benchmarks"].items()}
            player_properties.update(benchmarks_properties)
            simplified_match["players"].append(player_properties)
        result.append(simplified_match)
    return result


def get_matches(count, start_match_id=None, patch=53, min_duration=1200, lobby_type=7):
    result = []
    less_than_match_id = start_match_id
    while len(result) < count:
        matches = get_parsed_matches_ids(less_than_match_id)
        time.sleep(1.01)
        if matches is None:
            continue
        less_than_match_id = matches[-1]["match_id"]
        for match in matches:
            loaded_match = get_match_by(match["match_id"])
            time.sleep(1.01)
            if loaded_match is None:
                continue
            if loaded_match["patch"] == patch and \
                    loaded_match["duration"] >= min_duration and \
                    loaded_match["lobby_type"] == lobby_type:
                result.append(loaded_match)
                print(f"Adding match is DONE with id {match['match_id']}")
    return result, less_than_match_id
