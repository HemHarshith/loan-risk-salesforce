"""Shared helpers: the fairness script and the tests both import these,
so they always use exactly the same data loading, split and model."""
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_FILE = Path("data/german_credit.csv")
RANDOM_STATE = 42   # fixed seed so every run gives the same split (reproducible)


def load_data():
    """Read the saved CSV. If it is missing (for example on GitHub's test machine),
    download the same dataset from OpenML and build the 0/1 'default' column."""
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    from sklearn.datasets import fetch_openml
    raw = fetch_openml("credit-g", version=1, as_frame=True)
    df = raw.frame.copy()
    df["default"] = (df["class"] == "bad").astype(int)
    return df.drop(columns="class")


def split(df):
    """80/20 split. stratify keeps the 30% default rate the same in both parts."""
    X, y = df.drop(columns="default"), df["default"]
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)


def build_model(X):
    """Pipeline = scale numbers + one-hot encode text + logistic regression.
    Keeping all steps in one Pipeline stops test data from leaking into training."""
    num = X.select_dtypes(include="number").columns
    cat = X.select_dtypes(exclude="number").columns
    prep = ColumnTransformer([("num", StandardScaler(), num),
                              ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    return Pipeline([("pre", prep), ("clf", LogisticRegression(max_iter=1000))])


def cutoff_from_cost(miss_cost, false_alarm_cost=1):
    """Best cut-off when missing a defaulter costs 'miss_cost' times a false alarm.
    Flag a loan when miss_cost * p > false_alarm_cost * (1 - p), i.e. p > 1 / (ratio + 1)."""
    return false_alarm_cost / (miss_cost + false_alarm_cost)