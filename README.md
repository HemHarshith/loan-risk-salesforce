# Loan Default Risk Scoring + Salesforce

A small end-to-end project: a machine learning model scores loan applications for default risk in **Python**, and the scores flow into **Salesforce** (Apex REST, Lightning Web Component, Platform Event, Batch Apex, Visualforce) where a loan officer would act on them.

Built as a personal learning project on a Salesforce Developer Edition org. It uses a public dataset only. No client or employer data is used.

## What it does

```
German Credit data -> Python model -> risk score (0 to 1)
        -> Apex REST endpoint -> Loan_Application__c record + risk band
        -> Loan Risk Card (LWC) on the record page
        -> High-risk loans publish a Platform Event -> review Task created
        -> Batch Apex re-bands all loans when the cut-off changes
        -> Visualforce summary page
```

## Results

| Metric | Value |
|---|---|
| Data | 1,000 loans, 20 features, 30% defaulters |
| 5-fold cross-validated AUC | 0.771 (+/- 0.053) |
| Hold-out test AUC (200 loans) | 0.804 |
| At threshold 0.5 | accuracy 0.78, precision 0.667, recall 0.533 |
| At cost-based threshold 0.15 | precision 0.411, recall 0.883 |
| Cost per loan (miss = 5, false alarm = 1) | 0.555, vs 1.5 approving everyone and 0.7 flagging everyone |

Predicting "no default" for everyone already gives 70% accuracy, so accuracy alone is misleading here. AUC, precision and recall are used instead.

## Project structure

```
src/        Python scripts 01 to 07 and shared helpers (model_utils.py)
tests/      pytest tests for the data and model
salesforce/ Salesforce DX project (object, fields, Apex, LWC, Platform Event, Visualforce)
reports/    ROC curve
practice/   early Python practice files
```

| Script | Purpose |
|---|---|
| `01_load_and_check.py` | Download data, check shape, missing values, duplicates, default rate |
| `02_baseline_model.py` | Logistic regression pipeline, AUC, metrics at several thresholds |
| `03_threshold_and_cv.py` | Cross-validation, cost-based threshold, ROC curve |
| `04_sql_analysis.py` | Load data into SQLite and analyse default rates with SQL |
| `05_create_sfdx_metadata.py` | Generate the Salesforce object, fields and permission set |
| `06_push_scores.py` | Train the model and send scores to the Apex REST endpoint |
| `07_fairness_check.py` | Compare flag rate, recall and precision by age band |

## How to run

**Python** (Python 3.12 or newer)
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\01_load_and_check.py
python -m pytest -q
```
The dataset (OpenML `credit-g`, the German Credit data) is downloaded by script 01. It is not stored in the repo.

**Salesforce** (a personal Developer Edition org, alias `devorg`)
```
sf org login web --alias devorg
cd salesforce
sf project deploy start --source-dir force-app --target-org devorg --test-level RunLocalTests
sf org assign permset --name Loan_Risk_Access --target-org devorg
sf org assign permset --name High_Risk_Loan_Events --target-org devorg
cd ..
python src\06_push_scores.py
sf org open --path /apex/LoanRiskSummary --target-org devorg
```
Add the **Loan Risk Card** component to the Loan Application record page in Lightning App Builder.

## Salesforce components

| Component | What it does |
|---|---|
| `Loan_Application__c` | Custom object with age, amount, duration, purpose, risk score and risk band |
| `LoanScoreService` (Apex REST) | Receives scored loans as JSON, validates, bulk-inserts, sets the band, publishes events |
| `loanRiskCard` (LWC) | Shows risk percentage, band badge and advice on the record page |
| `High_Risk_Loan__e` + `HighRiskLoanTrigger` | Platform Event and subscriber that create a review Task for High-band loans |
| `LoanBandBatch` | Batch Apex job that re-bands all loans for new cut-offs, in chunks of 200 |
| `LoanRiskSummary` (Visualforce) | Counts by band and the 10 highest-risk loans |
| Apex tests | Cover the endpoint, event flow, batch job and Visualforce controller (coverage: 97% | 100% | 100% | 100% ) 

## Model card

**Intended use.** Demonstrate how a credit-risk score can be produced, evaluated and surfaced in a CRM. It is not validated for real lending decisions.

**Data.** German Credit (Statlog) dataset from OpenML, 1,000 loans from the 1990s. Small, old and from one country, so it does not represent current applicants.

**Model.** Logistic regression in a scikit-learn Pipeline (standard scaling for numbers, one-hot encoding for categories). Chosen because it is simple and easy to explain.

**Evaluation.** Stratified 80/20 split with a fixed random seed, plus 5-fold cross-validation. The cross-validated AUC (0.771) is the figure to quote, because a single 200-loan test set is noisy.

**Threshold and cost.** The cut-off of 0.15 comes from an assumed cost where missing a defaulter is 5 times worse than a false alarm (the dataset's own cost guideline). Cut-off = 1 / (ratio + 1) in theory, about 0.17, and the grid search chose 0.15. A real lender would use its own cost figures and weight by loan amount.

**Fairness check.** At the 0.15 cut-off the model flags younger applicants more often:

| Age band | Loans | Flag rate | Recall | Precision |

| under 25 |   39  |    77%    |  0.947 |   0.600   |
| 25-34    |   66  |    67%    |  0.864 |   0.432   |
| 35-49    |   63  |    59%    |  0.923 |   0.324   |
| 50+      |   32  |    56%    |  0.667 |   0.222   |

The lowest-to-highest flag-rate ratio is 0.73. Part of the gap reflects higher default rates among younger borrowers in this sample, and the groups are small, so no firm conclusion can be drawn. Age is also a model input, which a real lender may not be allowed to use. A next step would be retraining without age and comparing results.

**Limitations.**
- Small, old dataset; results are noisy and may not transfer.
- The cost ratio is an assumption.
- Probabilities are not calibrated or monitored over time.
- Salesforce scores here come from the held-out test loans for demonstration, not live applications.
- Not a decision system: flagged loans are for human review, not automatic rejection.

## Skills demonstrated

Python (pandas, scikit-learn, matplotlib, sqlite3), SQL, model evaluation (AUC, precision, recall, cross-validation, threshold tuning), pytest and GitHub Actions, Apex (REST, triggers, Batch, test classes), Platform Events, Lightning Web Components, Visualforce, Salesforce DX and CLI, permission sets and field-level security.
