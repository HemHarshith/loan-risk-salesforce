from pathlib import Path
import pandas as pd
from sklearn.datasets import fetch_openml

DATA = Path("data")
DATA.mkdir(exist_ok=True)

def load():
    raw = fetch_openml("credit-g", version=1, as_frame=True)
    df = raw.frame.copy()
    df["default"] = (df["class"] == "bad").astype(int)  # 1 = defaulter
    return df.drop(columns="class")

def quality_report(df):
    print("shape:", df.shape)
    print("missing per column:\n", df.isna().sum()[lambda s: s > 0])
    print("duplicate rows:", df.duplicated().sum())
    print("default rate:", round(df["default"].mean(), 3))
    print("numeric cols:", df.select_dtypes("number").shape[1],
          "| categorical cols:", df.select_dtypes(exclude="number").shape[1])
    print(df.describe().T[["min", "mean", "max"]])

if __name__ == "__main__":
    df = load()
    quality_report(df)
    df.to_csv(DATA / "german_credit.csv", index=False)