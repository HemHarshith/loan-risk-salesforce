from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.read_csv("data/german_credit.csv")
X, y = df.drop(columns="default"), df["default"]
num = X.select_dtypes(include="number").columns
cat = X.select_dtypes(exclude="number").columns
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

pre = ColumnTransformer([("num", StandardScaler(), num),
                         ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
print(f"5-fold CV AUC: {scores.mean():.3f} (+/- {scores.std():.3f})")

# Choose the threshold on training data only (out-of-fold predictions)
oof = cross_val_predict(model, X_train, y_train, cv=cv, method="predict_proba")[:, 1]
COST_FN, COST_FP = 5, 1  # missing a defaulter costs 5x a wrongly rejected good loan
def cost(y_true, proba, t):
    pred = proba >= t
    fn = ((~pred) & (y_true.values == 1)).sum()
    fp = (pred & (y_true.values == 0)).sum()
    return COST_FN * fn + COST_FP * fp
grid = np.arange(0.10, 0.90, 0.05)
best_t = min(grid, key=lambda t: cost(y_train, oof, t))
print("best threshold on training data:", round(best_t, 2))

# Final check on the untouched test set
model.fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]
pred = proba >= best_t
print("test AUC:", round(roc_auc_score(y_test, proba), 3))
print("test precision:", round(precision_score(y_test, pred), 3),
      "| recall:", round(recall_score(y_test, pred), 3))
print("test cost per loan:", round(cost(y_test, proba, best_t) / len(y_test), 3))

Path("reports").mkdir(exist_ok=True)
RocCurveDisplay.from_predictions(y_test, proba)
plt.title("ROC curve - logistic regression (test set)")
plt.savefig("reports/roc_curve.png", dpi=150, bbox_inches="tight")