import random
import json
import pickle
from parsing.matches.get_matches import simplify
from parsing.heroes.heroes_properties import HeroesProperties
import pandas as pd

simplified_statistic_matches = []
for index in range(33):
    with open(f"loaded_matches/matches_butch_{index}.json", "r") as json_file:
        simplified_statistic_matches += simplify(*(json.load(json_file)))

statistics_size = int(0.6 * len(simplified_statistic_matches))
random.shuffle(simplified_statistic_matches)
statistic = simplified_statistic_matches[:statistics_size]
train = simplified_statistic_matches[statistics_size:]

with open(f"simplified_matches/statistic.json", "w") as json_file:
    json.dump(statistic, json_file)

with open(f"simplified_matches/train.json", "w") as json_file:
    json.dump(train, json_file)

heroes_properties = HeroesProperties(*statistic)
with open("../../model/heroes_properties.pickle", "wb") as file:
    pickle.dump(heroes_properties, file)

