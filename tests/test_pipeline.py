"""Automatic checks for the data and model. Run with: python -m pytest -q
If someone changes the data or the code and breaks something, a test fails straight away."""
import pytest
from sklearn.metrics import roc_auc_score

from model_utils import build_model, cutoff_from_cost, load_data, split


@pytest.fixture(scope="module")   # built once and reused by the tests below (faster)
def fitted():
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)
    model = build_model(X_train)
    model.fit(X_train, y_train)
    return df, model, X_train, X_test, y_train, y_test


def test_data_is_clean(fitted):
    df = fitted[0]
    assert df.shape == (1000, 21)          # 1000 loans, 20 features + the target
    assert df.isna().sum().sum() == 0      # no missing values
    assert df.duplicated().sum() == 0      # no duplicate rows


def test_default_rate_is_about_30_percent(fitted):
    assert abs(fitted[0]["default"].mean() - 0.30) < 0.01


def test_split_keeps_default_rate(fitted):
    _, _, _, _, y_train, y_test = fitted
    assert abs(y_train.mean() - y_test.mean()) < 0.02   # stratify worked


def test_scores_are_probabilities(fitted):
    _, model, _, X_test, _, _ = fitted
    scores = model.predict_proba(X_test)[:, 1]
    assert scores.min() >= 0 and scores.max() <= 1


def test_model_beats_random_guessing(fitted):
    _, model, _, X_test, _, y_test = fitted
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    assert auc > 0.70    # 0.5 would be random; we saw about 0.80


def test_cutoff_formula():
    assert cutoff_from_cost(1) == pytest.approx(0.5)        # equal costs: the usual 0.5
    assert cutoff_from_cost(5) == pytest.approx(1 / 6)      # 5:1 gives about 0.167