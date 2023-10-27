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

baseline_features = ["counter_picks", "synergy_picks"]
drop_features = ["lane_efficiency", "hero_healing_per_min", "net_worth"]

all_matches = []
for index in range(10):
    with open(f"../parsing/matches/simplified_matches_butch_{index}.json", "r") as json_file:
        all_matches += json.load(json_file)


train_matches, val_matches = train_test_split(all_matches, train_size=0.8, random_state=42, shuffle=True)

# heroes_properties = HeroesProperties(*train_matches)
# with open("heroes_properties.pickle", "wb") as file:
#     pickle.dump(heroes_properties, file)
with open("heroes_properties.pickle", "rb") as file:
    heroes_properties = pickle.load(file)

radiant_picks, dire_picks = take_picks(*train_matches)
train_features = preprocess(radiant_picks, dire_picks, heroes_properties).drop(columns=drop_features)
train_target = np.array([match["radiant_win"] for match in train_matches]).astype(int)

# baseline_features = train_features[baseline_features]
# baseline_target = train_target

radiant_picks, dire_picks = take_picks(*val_matches)
val_features = preprocess(radiant_picks, dire_picks, heroes_properties).drop(columns=drop_features)
val_target = np.array([match["radiant_win"] for match in val_matches]).astype(int)


xgb_train = xgb.DMatrix(train_features.values, train_target, feature_names=list(train_features.columns))
xgb_val = xgb.DMatrix(val_features.values, val_target, feature_names=list(val_features.columns))
# xgb_baseline = xgb.DMatrix(baseline_features, baseline_target, feature_names=list(baseline_features.columns))

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

    "max_depth": 10,
    "max_leaves": 40,
    "subsample": 0.7,
    "colsample_bytree": 0.7,

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

    "max_depth": 10,
    "max_leaves": 40,
    "subsample": 0.7,
    "colsample_bytree": 0.7,

    "tree_method": "hist",
    "grow_policy": "lossguide"
}

# baseline_model = xgb.train(params=baseline_parameters,
#                            dtrain=xgb_baseline,
#                            num_boost_round=1000,
#                            evals=[(xgb_val, "validation")],
#                            early_stopping_rounds=50)
model = xgb.train(params=model_parameters,
                  dtrain=xgb_train,
                  num_boost_round=1000,
                  evals=[(xgb_train, "train"), (xgb_val, 'val')],
                  early_stopping_rounds=50)

print(model.best_iteration)
print(accuracy_score(val_target, np.round(model.predict(xgb_val)).astype(int)))

# Отримати важливість ознак
importance = model.get_fscore()

# Створити сортований список ознак за важливістю
sorted_importance = sorted(importance.items(), key=lambda x: x[1])

# Розпакувати імена ознак і їх важливості
features, importances = zip(*sorted_importance)

# Відобразити графік важливості ознак
plt.figure(figsize=(10, 8))
plt.barh(range(len(features)), importances, align='center')
plt.yticks(range(len(features)), features)
plt.xlabel('Важливість ознак')
plt.title('Графік важливості ознак')
plt.show()

model = xgb.train(params=model_parameters,
                  dtrain=xgb_train,
                  num_boost_round=max(1, model.best_iteration))
print(accuracy_score(val_target, np.round(model.predict(xgb_val)).astype(int)))

# Отримати важливість ознак
importance = model.get_fscore()

# Створити сортований список ознак за важливістю
sorted_importance = sorted(importance.items(), key=lambda x: x[1])

# Розпакувати імена ознак і їх важливості
features, importances = zip(*sorted_importance)

# Відобразити графік важливості ознак
plt.figure(figsize=(10, 8))
plt.barh(range(len(features)), importances, align='center')
plt.yticks(range(len(features)), features)
plt.xlabel('Важливість ознак')
plt.title('Графік важливості ознак')
plt.show()
