from parsing.heroes.heroes_properties import HeroesProperties
import numpy as np
import pandas as pd


def take_picks(*simpled_matches):
    picks = {
        "radiant": [[player["hero_id"] for player in match["players"][:5]] for match in simpled_matches],
        "dire": [[player["hero_id"] for player in match["players"][5:]] for match in simpled_matches]
    }
    return picks["radiant"], picks["dire"]


def preprocess(radiant_picks, dire_picks, hero_properties: HeroesProperties):
    result = pd.DataFrame()
    result[hero_properties.additive_properties.columns] = np.array(
        [hero_properties.additive_properties.loc[radiant_pick].sum().values
         for radiant_pick in radiant_picks]) - np.array([hero_properties.additive_properties.loc[dire_pick].sum().values
                                                         for dire_pick in dire_picks])
    result["counter_picks"] = np.array(
        [hero_properties.counter_picks.loc[radiant_pick][dire_pick].sum().sum() for radiant_pick, dire_pick in
         zip(radiant_picks, dire_picks)]) - np.array(
        [hero_properties.counter_picks.loc[dire_pick][radiant_pick].sum().sum() for radiant_pick, dire_pick in
         zip(radiant_picks, dire_picks)])
    result["synergy_picks"] = np.array(
        [hero_properties.synergy_picks.loc[radiant_pick][dire_pick].sum().sum() for radiant_pick, dire_pick in
         zip(radiant_picks, dire_picks)]) - np.array(
        [hero_properties.counter_picks.loc[dire_pick][radiant_pick].sum().sum() for radiant_pick, dire_pick in
         zip(radiant_picks, dire_picks)])
    return result
