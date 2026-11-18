"""Fairness check: does the model treat age groups differently at our 0.15 cut-off?
Idea: compare how often each group is flagged, and how well we catch defaulters in each group."""
import pandas as pd
from sklearn.metrics import precision_score, recall_score

from model_utils import build_model, load_data, split

THRESHOLD = 0.15   # cost-based cut-off chosen in script 03

df = load_data()
X_train, X_test, y_train, y_test = split(df)
model = build_model(X_train)
model.fit(X_train, y_train)
scores = model.predict_proba(X_test)[:, 1]          # probability of default per test loan

# One row per test loan: age, what really happened, and whether the model flagged it.
report = pd.DataFrame({
    "age": X_test["age"].values,
    "actual": y_test.values,
    "flagged": (scores >= THRESHOLD).astype(int),
})
# pd.cut puts each age into a band: (0,24] = under 25, (24,34] = 25-34, and so on.
report["age_band"] = pd.cut(report["age"], bins=[0, 24, 34, 49, 120],
                            labels=["<25", "25-34", "35-49", "50+"])

rows = []
for band, g in report.groupby("age_band", observed=True):
    rows.append({
        "age_band": band,
        "loans": len(g),
        "defaulters": int(g["actual"].sum()),
        "flag_rate": g["flagged"].mean(),    # share of this group the model flags for review
        # recall = share of this group's real defaulters we caught
        "recall": recall_score(g["actual"], g["flagged"], zero_division=0),
        # precision = share of flagged people in this group who really defaulted
        "precision": precision_score(g["actual"], g["flagged"], zero_division=0),
    })
table = pd.DataFrame(rows).round(3)
print(table.to_string(index=False))

# Ratio of the lowest to the highest flag rate. A common screening rule of thumb
# is that a ratio far below about 0.8 deserves a closer look (it is a prompt to
# investigate, not proof of unfairness).
ratio = table["flag_rate"].min() / table["flag_rate"].max()
print("\nflag-rate ratio (lowest / highest):", round(ratio, 2))
print("Caution: each group has only a few dozen loans in the test set, so these numbers are noisy.")