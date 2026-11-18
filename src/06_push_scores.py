import json
import shutil
import subprocess

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ORG_ALIAS = "devorg"

def train_and_score():
    """Rebuild the same model as script 03 and score the 200 held-out test loans.
    Using the same random_state=42 gives the identical split, so results match earlier scripts."""
    df = pd.read_csv("data/german_credit.csv")
    X, y = df.drop(columns="default"), df["default"]
    num = X.select_dtypes(include="number").columns
    cat = X.select_dtypes(exclude="number").columns
    X_train, X_test, y_train, _ = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)
    pre = ColumnTransformer([("num", StandardScaler(), num),
                             ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
    model.fit(X_train, y_train)
    scores = model.predict_proba(X_test)[:, 1]   # column 1 = probability of default
    return X_test.assign(score=scores)


def build_payload(scored):
    """Convert the table into the JSON shape the Apex endpoint expects.
    The keys (age, creditAmount, ...) must match the Apex LoanInput class exactly."""
    loans = [{
        "age": int(r.age),
        "creditAmount": float(r.credit_amount),
        "durationMonths": int(r.duration),
        "purpose": str(r.purpose),
        "riskScore": round(float(r.score), 3),
    } for r in scored.itertuples()]
    return {"loans": loans}


if __name__ == "__main__":
    payload = build_payload(train_and_score())

    # "sf api request rest" makes the HTTP call for us using the login stored by the CLI.
    # --body "-" means "read the JSON body from standard input", which we feed with input=.
    sf = shutil.which("sf")
    result = subprocess.run(
        [sf, "api", "request", "rest", "/services/apexrest/loanscore",
         "--method", "POST", "--body", "-", "--target-org", ORG_ALIAS],
        input=json.dumps(payload), capture_output=True, text=True)

    print("exit code:", result.returncode)            # 0 = success
    print((result.stdout or result.stderr)[:600])     # first part of the reply or the error