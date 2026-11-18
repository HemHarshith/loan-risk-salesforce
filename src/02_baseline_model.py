import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

df = pd.read_csv("data/german_credit.csv")
X, y = df.drop(columns="default"), df["default"]
num = X.select_dtypes(include="number").columns
cat = X.select_dtypes(exclude="number").columns

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

pre = ColumnTransformer([
    ("num", StandardScaler(), num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)[:, 1]
print("AUC:", round(roc_auc_score(y_test, proba), 3))
print("accuracy if we label everyone 'no default':", round(1 - y_test.mean(), 3))

for t in [0.5, 0.4, 0.3, 0.2]:
    pred = (proba >= t).astype(int)
    print(f"threshold {t}: accuracy {accuracy_score(y_test, pred):.3f}, "
          f"precision {precision_score(y_test, pred, zero_division=0):.3f}, "
          f"recall {recall_score(y_test, pred):.3f}")