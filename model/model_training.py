import numpy as np
import xgboost as xgb
import json
import pickle
from parsing.matches.get_matches import simplify
from parsing.preprocessing import preprocess, take_picks
from parsing.heroes.heroes_properties import HeroesProperties
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


drop_features = ["lane_efficiency", "hero_healing_per_min", "net_worth"]

all_matches = []
for index in range(10):
    with open(f"../parsing/matches/simplified_matches_butch_{index}.json", "r") as json_file:
        all_matches += json.load(json_file)

with open('../common/heroes.json', 'r') as file:
    heroes_data = json.load(file)

train_matches, val_matches = train_test_split(all_matches, train_size=0.8, random_state=42, shuffle=True)

with open("heroes_properties.pickle", "rb") as file:
    heroes_properties = pickle.load(file)

radiant_picks, dire_picks = take_picks(*train_matches)
train_features = preprocess(radiant_picks, dire_picks, heroes_properties).drop(columns=drop_features)
train_target = np.array([match["radiant_win"] for match in train_matches]).astype(int)
xgb_train = xgb.DMatrix(train_features.values, train_target, feature_names=list(train_features.columns))

model_parameters = {
    "objective": "binary:logistic",
    "eta": 0.1,
    "lambda": 0.1,
    "alpha": 0.1,
    "gamma": 0.1,
    "verbosity": 0,
    "nthread": 20,
    "random_seed": 42,
    "eval_metric": 'error',

    "max_depth": 10,
    "max_leaves": 40,
    "subsample": 0.7,
    "colsample_bytree": 0.7,

    "tree_method": "hist",
    "grow_policy": "lossguide"
}

model = xgb.train(params=model_parameters,
                  dtrain=xgb_train,
                  num_boost_round=1)
model.save_model("model")
