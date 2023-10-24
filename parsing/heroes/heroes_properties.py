import numpy as np
import pandas as pd
import json

ADDITIVE_PROPERTIES_NAMES = ["assists", "deaths", "firstblood_claimed",
                             "gold_per_min", "hero_damage", "hero_healing", "hero_id", "kills", "last_hits",
                             "net_worth", "stuns", "teamfight_participation", "tower_damage", "xp_per_min",
                             "duration", "win", "kda", "courier_kills",
                             "ancient_kills", "lane_efficiency"]

with open('common/heroes.json', 'r') as file:
    heroes_data = json.load(file)


class HeroesProperties:
    def __init__(self, *simpled_matches):
        self.additive_properties: pd.DataFrame = self._get_additive_properties(*simpled_matches)
        self.counter_picks: pd.DataFrame = self._get_counter_picks(*simpled_matches)
        self.synergy_picks: pd.DataFrame = self._get_synergy_picks(*simpled_matches)

    @staticmethod
    def _get_additive_properties(*simpled_matches):
        heroes_properties = {}
        for property_name in ADDITIVE_PROPERTIES_NAMES:
            heroes_properties[property_name] = [player[property_name] for simpled_match in simpled_matches
                                                for player in simpled_match["players"]]
        dt = pd.DataFrame(heroes_properties, columns=ADDITIVE_PROPERTIES_NAMES).set_index('hero_id')
        unique_heroes = dt.groupby("hero_id").mean()
        return unique_heroes

    @staticmethod
    def _get_counter_picks(*simpled_matches):
        picks = {
            "match_id": [match["match_id"] for match in simpled_matches],
            "radiant_win": [int(match["radiant_win"]) for match in simpled_matches],
            "radiant": [[player["hero_id"] for player in match["players"][:5]] for match in simpled_matches],
            "dire": [[player["hero_id"] for player in match["players"][5:]] for match in simpled_matches]
        }
        picks_df = pd.DataFrame(picks).set_index("match_id")

        all_heroes = [hero["id"] for hero in heroes_data.values()]

        result_df = pd.DataFrame(index=all_heroes, columns=all_heroes)
        result_df = result_df.fillna(0.0)

        for hero1 in all_heroes:
            radiant_matches_results = \
                picks_df[picks_df.apply(lambda raw: hero1 in raw["radiant"], axis=1)][
                    "radiant_win"]
            dire_matches_results = 1 - picks_df[
                picks_df.apply(lambda raw: hero1 in raw["dire"], axis=1)]["radiant_win"]
            absolute_win_rate = pd.concat([radiant_matches_results, dire_matches_results]).mean()
            if np.isnan(absolute_win_rate):
                absolute_win_rate = 0.5
            for hero2 in all_heroes:
                radiant_common_matches_results = \
                    picks_df[picks_df.apply(lambda raw: hero1 in raw["radiant"] and hero2 in raw["dire"], axis=1)][
                        "radiant_win"]
                dire_common_matches_results = 1 - picks_df[
                    picks_df.apply(lambda raw: hero1 in raw["dire"] and hero2 in raw["radiant"], axis=1)]["radiant_win"]
                relative_win_rate = pd.concat([radiant_common_matches_results, dire_common_matches_results]).mean()
                if np.isnan(relative_win_rate):
                    relative_win_rate = 0.5
                result_df.at[hero1, hero2] = relative_win_rate - absolute_win_rate
        return result_df

    @staticmethod
    def _get_synergy_picks(*simpled_matches):
        picks = {
            "match_id": [match["match_id"] for match in simpled_matches],
            "radiant_win": [int(match["radiant_win"]) for match in simpled_matches],
            "radiant": [[player["hero_id"] for player in match["players"][:5]] for match in simpled_matches],
            "dire": [[player["hero_id"] for player in match["players"][5:]] for match in simpled_matches]
        }
        picks_df = pd.DataFrame(picks).set_index("match_id")

        all_heroes = [hero["id"] for hero in heroes_data.values()]

        result_df = pd.DataFrame(index=all_heroes, columns=all_heroes)
        result_df = result_df.fillna(0.0)

        for hero1 in all_heroes:
            radiant_matches_results = \
                picks_df[picks_df.apply(lambda raw: hero1 in raw["radiant"], axis=1)][
                    "radiant_win"]
            dire_matches_results = 1 - picks_df[
                picks_df.apply(lambda raw: hero1 in raw["dire"], axis=1)]["radiant_win"]
            absolute_win_rate = pd.concat([radiant_matches_results, dire_matches_results]).mean()
            if np.isnan(absolute_win_rate):
                absolute_win_rate = 0.5
            for hero2 in all_heroes:
                radiant_common_matches_results = \
                    picks_df[picks_df.apply(lambda raw: hero1 in raw["radiant"] and hero2 in raw["radiant"], axis=1)][
                        "radiant_win"]
                dire_common_matches_results = 1 - picks_df[
                    picks_df.apply(lambda raw: hero1 in raw["dire"] and hero2 in raw["dire"], axis=1)]["radiant_win"]
                relative_win_rate = pd.concat([radiant_common_matches_results, dire_common_matches_results]).mean()
                if np.isnan(relative_win_rate):
                    relative_win_rate = 0.5
                result_df.at[hero1, hero2] = absolute_win_rate - relative_win_rate
        return result_df
