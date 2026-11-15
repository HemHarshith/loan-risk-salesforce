"""
ds_syntax_tour.py - one runnable file covering the Python you need for data science.

Install once (in your project folder, with the venv active):
    pip install pandas numpy matplotlib scikit-learn

Run:  python ds_syntax_tour.py
Each PART prints its own heading. Read the code, run it, change a value, run again.
Everything uses made-up loan data, so no downloads are needed.
"""

# ---------------------------------------------------------------- PART 1: core syntax
print("\n=== PART 1: core syntax ===")

# variables, f-strings, number formatting
loan, rate, years = 800_000, 0.11, 5
print(f"Loan {loan:,} at {rate:.1%} for {years} years")        # 800,000 ... 11.0%

# list, tuple, dict, set
amounts = [250_000, 500_000, 800_000]            # list: ordered, changeable
point = (3, 4)                                   # tuple: ordered, fixed
customer = {"id": 101, "name": "Asha", "score": 710}   # dict: key -> value
grades = {"A", "B", "A"}                         # set: unique values only
customer["score"] += 10                          # update a value
print(amounts[-1], point[0], customer["name"], grades)

# if / elif / else
score = customer["score"]
if score >= 750:
    band = "low risk"
elif score >= 650:
    band = "medium risk"
else:
    band = "high risk"
print("band:", band)

# loops, enumerate, zip, range
for i, amt in enumerate(amounts, start=1):
    print(i, amt)
for name, s in zip(["Asha", "Ravi"], [710, 640]):
    print(name, s)
total = 0
while total < 3:
    total += 1

# comprehensions (very common in data work)
squares = [x ** 2 for x in range(5)]
big_loans = [a for a in amounts if a > 300_000]
by_name = {c: len(c) for c in ["Asha", "Ravi"]}
print(squares, big_loans, by_name)

# functions: default args, return values, lambda
def emi(principal, annual_rate, months=60):
    """Monthly instalment on a loan (standard EMI formula)."""
    r = annual_rate / 12
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)

print("EMI:", round(emi(800_000, 0.11), 2))
double = lambda x: x * 2
print(sorted(amounts, key=lambda a: -a))        # sort descending with a lambda

# classes (read other people's code; you rarely write many)
class Loan:
    def __init__(self, amount, rate):
        self.amount = amount
        self.rate = rate

    def yearly_interest(self):
        return self.amount * self.rate

print(Loan(500_000, 0.09).yearly_interest())

# errors, files, modules
try:
    int("abc")
except ValueError as e:
    print("caught:", e)

with open("demo.txt", "w") as f:                # 'with' closes the file for you
    f.write("hello\n")
with open("demo.txt") as f:
    print(f.read().strip())

import math, random, json, os                   # standard-library modules
print(math.sqrt(16), json.dumps(customer), os.path.exists("demo.txt"))


# ---------------------------------------------------------------- PART 2: numpy
print("\n=== PART 2: numpy ===")
import numpy as np

rng = np.random.default_rng(42)                 # seeded generator = repeatable results
a = np.array([1, 2, 3, 4])
print(a * 2, a.mean(), a.std(), a.reshape(2, 2))
print(np.where(a > 2, "high", "low"))           # vectorised if/else
x = rng.normal(loc=50, scale=10, size=5)
print(x.round(1), x.max(), x.argmax())


# ---------------------------------------------------------------- PART 3: pandas
print("\n=== PART 3: pandas (made-up loan data) ===")
import pandas as pd

n = 2000
df = pd.DataFrame({
    "income":     rng.normal(60_000, 20_000, n).clip(15_000, None).round(0),
    "loan_amt":   rng.normal(250_000, 100_000, n).clip(20_000, None).round(0),
    "credit_score": rng.normal(680, 70, n).clip(300, 850).round(0),
    "age":        rng.integers(21, 66, n),
    "home":       rng.choice(["rent", "own", "mortgage"], n, p=[0.4, 0.2, 0.4]),
})
# a made-up rule for who defaults (about 1 in 10): low score, high loan-to-income -> higher chance
df["lti"] = df["loan_amt"] / df["income"]                       # new column
p = 1 / (1 + np.exp(-(-3.8 - 0.012 * (df["credit_score"] - 680) + 0.35 * df["lti"])))
df["default"] = (rng.random(n) < p).astype(int)

print(df.head(3))
print(df.shape, df.dtypes.to_dict())
print(df.describe().round(1))
print(df.isna().sum().sum(), "missing values")
print(df[df["credit_score"] < 600].shape[0], "loans under 600")   # filter rows
print(df.groupby("home")["default"].mean().round(3))             # group + aggregate
print(df.sort_values("loan_amt", ascending=False).head(2))
df["band"] = pd.cut(df["credit_score"], [0, 600, 700, 900], labels=["high", "medium", "low"])
print(pd.crosstab(df["band"], df["default"], normalize="index").round(3))
df = pd.get_dummies(df, columns=["home"], drop_first=True)       # text -> 0/1 columns
df.to_csv("loans_demo.csv", index=False)                         # save
df = pd.read_csv("loans_demo.csv")                               # load


# ---------------------------------------------------------------- PART 4: matplotlib
print("\n=== PART 4: matplotlib ===")
import matplotlib
matplotlib.use("Agg")           # save to files; remove this line to pop up windows
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].hist(df["credit_score"], bins=30)
ax[0].set_title("Credit score distribution")
df.groupby("band", observed=True)["default"].mean().plot.bar(ax=ax[1])
ax[1].set_title("Default rate by band")
plt.tight_layout()
plt.savefig("loan_charts.png", dpi=120)
print("saved loan_charts.png")


# ---------------------------------------------------------------- PART 5: scikit-learn
print("\n=== PART 5: scikit-learn mini pipeline ===")
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, classification_report

features = ["income", "loan_amt", "credit_score", "age", "lti", "home_own", "home_rent"]
X, y = df[features], df["default"]

# stratify keeps the default rate similar in train and test. Never judge on training data.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

for name, model in [
    ("logistic regression", LogisticRegression(max_iter=1000)),
    ("random forest", RandomForestClassifier(n_estimators=200, random_state=42)),
]:
    model.fit(X_train, y_train)
    prob = model.predict_proba(X_test)[:, 1]            # probability of default
    pred = (prob >= 0.5).astype(int)    # real defaults are rare, so recall is low at 0.5; later we tune this threshold
    print(f"\n{name}: AUC = {roc_auc_score(y_test, prob):.3f}")
    print(confusion_matrix(y_test, pred))
    print(classification_report(y_test, pred, digits=3))

# risk score + band for each test loan: this is what we will push into Salesforce
scored = X_test.copy()
scored["risk_score"] = (prob * 100).round(1)
scored["risk_band"] = pd.cut(scored["risk_score"], [-1, 20, 50, 100],
                             labels=["Low", "Medium", "High"])
print(scored[["risk_score", "risk_band"]].head())
print("\nDone. Next: replace the made-up data with a real dataset.")
