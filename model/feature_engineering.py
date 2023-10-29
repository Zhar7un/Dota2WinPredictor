import numpy as np
import xgboost as xgb
import json
import pickle
from parsing.preprocessing import preprocess, take_picks
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

baseline_features = ["counter_picks", "synergy_picks", "win"]
drop_features = ["move_speed", "last_hits_per_min", "hero_damage_per_min",
                 "gold_per_min", "kills_per_min", "attack_rate", "hero_healing_per_min", "lane_efficiency",
                 "lhten", "xp_per_min", "stuns_per_min", "deaths", "last_hits", "net_worth", "assists", "hero_healing",
                 "roshan_kills", "attack_range", "firstblood_claimed"]

with open("../parsing/matches/simplified_matches/train.json", "r") as file:
    train = json.load(file)

with open("heroes_properties.pickle", "rb") as file:
    heroes_properties = pickle.load(file)

radiant_picks, dire_picks = take_picks(*train)
train_features = preprocess(radiant_picks, dire_picks, heroes_properties).drop(columns=drop_features)
train_target = np.array([match["radiant_win"] for match in train]).astype(int)

baseline_features = train_features[baseline_features]
baseline_target = train_target

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
xgb_train = xgb.DMatrix(train_features.values, train_target, feature_names=list(train_features.columns))
xgb_baseline = xgb.DMatrix(baseline_features.values, baseline_target, feature_names=list(baseline_features.columns))

baseline_parameters = {
    "objective": "binary:logistic",
    "eta": 0.1,
    "lambda": 0.1,
    "alpha": 0.1,
    "gamma": 0.1,
    "verbosity": 0,
    "nthread": 20,
    "random_seed": 42,
    "eval_metric": 'error',

    "max_depth": 5,
    "max_leaves": 40,
    "subsample": 0.9,
    "colsample_bytree": 0.9,

    "tree_method": "hist",
    "grow_policy": "lossguide"
}

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

    "max_depth": 5,
    "max_leaves": 50,
    "subsample": 0.9,
    "colsample_bytree": 0.9,

    "tree_method": "hist",
    "grow_policy": "lossguide"
}

results = xgb.cv(model_parameters, xgb_train, num_boost_round=1000,
                 folds=skf, verbose_eval=10, metrics={'error'}, early_stopping_rounds=50)

num_round = results['test-error-mean'].idxmin()
print(num_round)
print(1 - results.iloc[num_round, 0], 1 - results.iloc[num_round, 2])
model = xgb.train(model_parameters, xgb_train, num_round)
model.save_model("model")

importance = model.get_fscore()
sorted_importance = sorted(importance.items(), key=lambda x: x[1])
features, importance = zip(*sorted_importance)

plt.figure(figsize=(10, 8))
plt.barh(range(len(features)), importance, align='center')
plt.yticks(range(len(features)), features)
plt.xlabel('Важливість ознак')
plt.title('Графік важливості ознак')
plt.show()

baseline_results = xgb.cv(baseline_parameters, xgb_baseline, num_boost_round=1000,
                          folds=skf, verbose_eval=10, metrics={'error'}, early_stopping_rounds=50)

num_round = baseline_results['test-error-mean'].idxmin()
print(num_round)
print(1 - baseline_results.iloc[num_round, 0], 1 - baseline_results.iloc[num_round, 2])
