import pickle

import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    VotingRegressor,
)
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from understatapi import UnderstatClient

import preprocessing.scrape_understat as su


def train_ml_player(train_data, field=True, use_grid_search=False):
    df = train_data.copy()

    df.index = df.ID
    df = df.loc[df.minutes >= 600]
    df = df.drop(["season", "minutes", "ID", "age"], axis=1)
    df = df.loc[df["games"] > 0]
    # Exclude specific column(s) from division
    if field == False:
        df.drop("Position", axis=1, inplace=True)
        columns_to_divide = df.columns.difference(["age", "games", "Points"])

    else:
        columns_to_divide = df.columns.difference(
            ["Position", "age", "games", "Points"]
        )

    df[columns_to_divide] = df[columns_to_divide].truediv(other=df["games"], axis=0)
    df["Points"] = df["Points"].truediv(other=df["games"], axis=0)
    y = df["Points"]
    X = df.drop(["Points", "games"], axis=1)

    feat_selector = VarianceThreshold(0.01)
    feat_selector.fit_transform(X)

    X = X[feat_selector.get_feature_names_out()]
    scaler = StandardScaler()
    X_val = scaler.fit_transform(X)
    X = pd.DataFrame(X_val, columns=scaler.get_feature_names_out())
    feat_importance = ExtraTreesRegressor().fit(X, y)
    feat_importance_ind = feat_importance.feature_importances_ > 0.001
    imp_feats = feat_importance.feature_names_in_[feat_importance_ind]
    X = X[imp_feats]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=17
    )
    if use_grid_search == True:
        nnml = MLPRegressor(max_iter=10000)
        if field == False:
            ml1 = HistGradientBoostingRegressor(max_iter=1000, l2_regularization=0.1)
        else:
            if "Position" in X.columns:
                ml1 = HistGradientBoostingRegressor(
                    categorical_features=["Position"],
                    max_iter=1000,
                    l2_regularization=2,
                )
            else:
                ml1 = HistGradientBoostingRegressor(max_iter=1000, l2_regularization=1)

        ml3 = RandomForestRegressor()

        ml4 = linear_model.Ridge()
        vote = VotingRegressor(
            estimators=[
                ("histgrad", ml1),
                ("randf", ml3),
                ("linear", ml4),
                ("nn", nnml),
            ]
        )
        params = {
            "histgrad__l2_regularization": [0, 0.5, 1, 2],
            "nn__alpha": [0.0001, 0.1],
            "nn__learning_rate": ["constant", "adaptive"],
            "linear__alpha": [1, 2],
            "randf__max_features": [1.0, 0.3],
            "randf__ccp_alpha": [0.0, 0.05, 0.01, 0.02],
        }
        grid = GridSearchCV(
            estimator=vote, param_grid=params, cv=4, verbose=1, return_train_score=True
        )

        grid = grid.fit(X_train, y_train)
        print(grid.score(X_test, y_test))
        cols_for_predict = X.columns
        return grid.best_estimator_, cols_for_predict, scaler
    else:
        nnml = MLPRegressor(max_iter=10000, alpha=0.1)
        if field == False:
            ml1 = HistGradientBoostingRegressor(max_iter=1000, l2_regularization=0)
        else:
            if "Position" in X.columns:
                ml1 = HistGradientBoostingRegressor(
                    categorical_features=["Position"],
                    max_iter=1000,
                    l2_regularization=0,
                )
            else:
                ml1 = HistGradientBoostingRegressor(max_iter=1000, l2_regularization=1)

        ml3 = RandomForestRegressor(ccp_alpha=0.05)

        ml4 = linear_model.Ridge(alpha=2)
        vote = VotingRegressor(
            estimators=[
                ("histgrad", ml1),
                ("randf", ml3),
                ("linear", ml4),
                ("nn", nnml),
            ]
        )
        vote = vote.fit(X_train, y_train)
        cols_for_predict = X.columns
        return vote, cols_for_predict, scaler


def load_team_data_us():
    us = UnderstatClient()
    c = 0
    for i in range(2014, 2023):
        leagues = ["Bundesliga", "EPL", "La_Liga", "Serie_A", "Ligue_1"]
        for league in leagues:
            temp_df = su.get_team_info(str(i), us, league=league)
            if c == 0:
                df = temp_df
            else:
                df = pd.concat([df, temp_df])
            c += 1
    return df


def train_ml_team(df, use_grid_search=False):
    df = df.reset_index(drop=True)
    # Drop 'team_id' here before any other operations
    df = df.drop("team_id", axis=1)
    ml_df_avg = df.div(df["games_played"], axis=0)

    y = ml_df_avg["pts"]
    X = ml_df_avg.drop(
        [
            "pts",
            "games_played",
            "xpts",
            "wins",
            "draws",
            "loses",
            "xG",
            "xGA",
            "scored",
            "missed",
        ],
        axis=1,
    )  # 'team_id' is already dropped
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=17
    )

    if use_grid_search == True:
        ml1 = HistGradientBoostingRegressor()
        ml2 = linear_model.Ridge()
        ml3 = RandomForestRegressor()
        vote = VotingRegressor(
            estimators=[
                ("histgrad", ml1),
                ("linear", ml2),
                ("randf", ml3),
            ]
        )
        params = {
            "histgrad__l2_regularization": [0, 0.5, 1, 2],
            "histgrad__max_leaf_nodes": [10, 20, 30, 40, 50],
            "linear__alpha": [0, 1, 2],
            "randf__max_features": [1.0, 0.3],
            "randf__ccp_alpha": [0.0, 0.05, 0.01, 0.02],
        }
        grid = GridSearchCV(
            estimator=vote, param_grid=params, cv=5, verbose=10, return_train_score=True
        )
        grid = grid.fit(X_train, y_train)
        print(grid.score(X_test, y_test))
        return (grid.best_estimator_,)

    else:
        ml1 = HistGradientBoostingRegressor(l2_regularization=0.5, max_leaf_nodes=10)
        ml2 = linear_model.Ridge(alpha=2)
        ml3 = RandomForestRegressor(max_features=0.3)
        vote = VotingRegressor(
            estimators=[
                ("histgrad", ml1),
                ("linear", ml2),
                ("randf", ml3),
            ]
        )
        vote = vote.fit(X_train, y_train)
        print(vote.score(X_test, y_test), " Team Pred Score")
        return vote


def predict_ml_team(model, pred_data):
    data = pred_data.copy()
    ind = data.team_title
    pts = data.pts
    X = data.drop(
        [
            "pts",
            "team_id",
            "team_title",
            "season",
            "xpts",
            "wins",
            "draws",
            "loses",
            "xG",
            "xGA",
            "scored",
            "missed",
        ],
        axis=1,
    )
    gp = X["games_played"]
    X = X.div(X["games_played"], axis=0)

    X = X.drop("games_played", axis=1)
    m_pred = model.predict(X)
    pred = (m_pred * (34 - gp)) + pts
    data["prediction"] = np.round(pred, 0)
    # Calculate strength score
    total_predicted_points = (m_pred * 34).sum()
    data["strength_score"] = np.round(((m_pred * 34) / total_predicted_points) * 100, 2)
    data.index = ind
    data.drop(columns=["team_title", "season"], inplace=True)
    return data


def predict_ml_player(predict_data, model, cols_for_predict, scaler):
    df = predict_data.copy()
    IDS = df.ID

    df = df.drop(["season"], axis=1)

    # Exclude specific column(s) from division
    columns_to_divide = df.columns.difference(["Position", "games", "Points"])
    # df[columns_to_divide] = df[columns_to_divide] * 100
    # Perform division only on the selected columns
    df[columns_to_divide] = df[columns_to_divide].truediv(other=df["games"], axis=0)

    y = df["Points"]
    X = df[cols_for_predict]
    fillnacols = X.columns.difference(["Position"])
    X[fillnacols] = X[fillnacols].fillna(0)
    X_val = scaler.transform(X)
    X = pd.DataFrame(X_val, columns=scaler.get_feature_names_out())
    new_pred_data = df.copy()
    # rest_predict = (model.predict(X) * 34) / new_pred_data["games"]
    # act_points_scaled = (new_pred_data["Points"] * 34) / new_pred_data["games"]
    number_of_games_played = new_pred_data.games.max()
    prediction = model.predict(X)
    new_pred_data["prediction"] = (
        prediction * (34 - number_of_games_played)
    ) + new_pred_data["Points"]

    new_pred_data["ID"] = IDS.astype("string")
    new_pred_data["ppg_exp"] = prediction
    return new_pred_data


def test_ml(predict_data, model, cols_for_predict):
    df = predict_data.copy()
    IDS = df.ID

    df = df.drop(["season"], axis=1)

    # Exclude specific column(s) from division
    columns_to_divide = df.columns.difference(["Position", "games", "Points"])
    # df[columns_to_divide] = df[columns_to_divide] * 100
    # Perform division only on the selected columns
    df[columns_to_divide] = df[columns_to_divide].truediv(other=df["games"], axis=0)

    y = df["Points"]
    X = df[cols_for_predict]
    fillnacols = X.columns.difference(["Position"])
    X[fillnacols] = X[fillnacols].fillna(0)
    scaler = StandardScaler()
    X_val = scaler.fit_transform(X)
    X = pd.DataFrame(X_val, columns=scaler.get_feature_names_out())
    new_pred_data = df.copy()
    # rest_predict = (model.predict(X) * 34) / new_pred_data["games"]
    # act_points_scaled = (new_pred_data["Points"] * 34) / new_pred_data["games"]
    number_of_games_played = new_pred_data.games.max()

    new_pred_data["prediction"] = (
        model.predict(X) * (34 - number_of_games_played)
    ) + new_pred_data["Points"]

    new_pred_data["ID"] = IDS.astype("string")
    y_test = new_pred_data["Points"] / new_pred_data["games"]
    print(model.score(X, y_test))
    return new_pred_data


if __name__ == "__main__":
    train_data = pd.read_csv("./data/train_field.csv")
    predict_data = pd.read_csv("./data/predict_field.csv")

    model, cols_for_predict, scaler = train_ml_player(train_data)

    with open("./preprocessing/model.pkl", "wb") as file:
        pickle.dump(model, file)

    with open("./preprocessing/cols_for_predict.pkl", "wb") as file:
        pickle.dump(cols_for_predict, file)

    with open("./preprocessing/scaler.pkl", "wb") as file:
        pickle.dump(scaler, file)

    team_ml_data_us = load_team_data_us()

    model_team = train_ml_team(use_grid_search=False, df=team_ml_data_us)

    team_pred_df = pd.read_csv("./data/df_us_team.csv")

    team_pred_df = team_pred_df.loc[team_pred_df.season.astype("str") == "2023"]

    team_predicted = predict_ml_team(model_team, team_pred_df)

    with open("./preprocessing/team_model.pkl", "wb") as file:
        pickle.dump(model_team, file)
