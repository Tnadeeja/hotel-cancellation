# Evaluation 2 Member Handover Guide

## 1. Purpose

Evaluation 2 is individually assessed within a group project. Each member has primary technical ownership of one algorithm family:

- Member A: Logistic Regression
- Member B: Decision Tree
- Member C: Random Forest
- Member D: Gradient Boosting / XGBoost family

Each member must make a substantial technical contribution to their assigned algorithm family. However, algorithm ownership does not mean that a student only studies their own algorithm. Every member must understand:

- the project problem and target
- the project novelty
- Evaluation 1 preprocessing and feature engineering
- leakage controls
- the fixed grouped outer holdout
- grouped inner CV
- common metrics and scoring conventions
- all four algorithms conceptually
- final model comparison and selection

## 2. Shared Foundation - Do Not Change

All members use the approved foundation and common protocol.

### Data and predictors

- Modelling population: 119,210 rows
- Target: `is_canceled`
- Positive class: `1 = Cancelled`
- Predictors: 30 unencoded features
- Numerical predictors: 20
- Categorical predictors: 10

Evaluation 1 removes only the 180 definitive zero-guest records, retains ambiguous duplicate-looking rows, and preserves the approved six source exclusions and five engineered features.

### Fixed outer holdout

- Outer training: 95,375 rows
- Outer test: 23,835 rows

The outer holdout is fixed. It must not be recreated with a new random split.

### Model-development training scopes

- General: 95,375 rows
- City: 63,044 rows
- Resort: 32,331 rows

City and Resort scopes come from the same approved outer split. Do not create separate random City or Resort holdouts.

### Common validation and scoring

Use:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)
```

The common primary metric is F1. Recall is the important secondary metric. Also report Accuracy, Precision, and ROC-AUC. Precision, Recall, and F1 use class `1` as the positive class, with `zero_division=0` where applicable.

Do not independently:

- create a new train/test split
- remove duplicate-looking rows
- alter row filtering
- alter the six source exclusions
- alter the five engineered features
- add `predictor_group` as a model feature
- change preprocessing logic
- use ordinary random CV
- preprocess all outer-training data before CV
- use the outer test set during tuning
- change the primary metric
- claim specialist superiority before evidence

## 3. Why Group-Aware CV Is Required

Exact duplicate-looking rows were retained because the dataset has no unique booking ID. Identical final predictor profiles must not cross model-development folds.

Predictor groups are created from the final unencoded predictor profile. The group hash is only a partition helper:

- it is not a booking ID
- it is not a customer ID
- it must never be passed as a predictor

All model-development CV must use the approved groups. Groups are supplied to the CV splitter or search procedure, while `X` contains only the approved named predictors.

Preprocessing must remain inside the sklearn `Pipeline`. Each CV training fold must learn its own:

- imputation values
- scaling statistics
- category vocabulary

The conceptual structure is:

```python
Pipeline([
    ("preprocessor", build_preprocessor(...)),
    ("classifier", estimator),
])
```

Do not fit a transformer on all outer-training rows before CV.

## 4. Three Required Modelling Scopes

Every algorithm owner works with all three scopes:

1. General
2. City-specific
3. Resort-specific

### General

Train using all outer-training bookings.

### City-specific

Train using only City Hotel rows from the outer-training population.

### Resort-specific

Train using only Resort Hotel rows from the outer-training population.

All three scopes preserve the common 30-predictor schema, including `hotel`. No separate random City/Resort holdouts are permitted.

## 5. Required Baseline Work for Each Member

Before tuning, each algorithm owner must create baseline experiments for General, City, and Resort.

Record for every baseline:

- algorithm name
- algorithm justification
- baseline parameters
- training scope
- training row count
- unique predictor-group count
- grouped five-fold CV strategy
- mean and standard deviation for Accuracy
- mean and standard deviation for Precision
- mean and standard deviation for Recall
- mean and standard deviation for F1
- mean and standard deviation for ROC-AUC
- observations
- likely strengths
- likely weaknesses

No hyperparameter tuning is allowed before baseline results are recorded and preserved.

## 6. Required Tuning Work for Each Member

After baseline completion, each owner must:

- identify meaningful hyperparameters
- explain what each selected hyperparameter controls
- define a justified search space
- choose an appropriate search method, such as GridSearchCV, RandomizedSearchCV, or another justified sklearn-compatible method
- use the same grouped inner CV
- supply groups during search fitting
- keep preprocessing inside the Pipeline
- use outer-training data only
- use F1 as the primary refit and selection metric unless the approved protocol is formally changed

Record:

- tuning method
- search space
- number of candidate configurations, if available
- best parameters
- best CV F1
- other common CV metrics
- baseline-versus-tuned comparison
- interpretation of whether tuning meaningfully helped

This handover document intentionally does not define algorithm-specific search spaces. Those belong to the individual algorithm owner during implementation.

## 7. Training-Only Novelty Comparison

Before inspecting outer-test results, compare modelling strategies using training-only out-of-fold evidence.

For each algorithm:

- General-model OOF predictions: calculate performance separately on City training rows and Resort training rows
- City-specific OOF predictions: calculate performance on City training rows
- Resort-specific OOF predictions: calculate performance on Resort training rows

Required development comparisons:

- General OOF on City versus City-specific OOF on City
- General OOF on Resort versus Resort-specific OOF on Resort

Rules:

- use only out-of-fold predictions
- never use in-sample predictions as validation evidence
- keep preprocessing inside each fold
- keep grouped CV active
- use outer-training data only
- keep the outer test untouched

Do not assume that hotel-specific modelling is superior. The evidence must determine the conclusion.

## 8. Final Outer-Test Evaluation Rule

Freeze the following using training-only evidence before evaluating the outer test:

- baseline analysis
- tuning
- algorithm configuration decisions
- General-versus-specialist development decisions

Then perform final evaluation on the untouched corresponding outer-test rows.

Required later comparisons include:

- General model evaluated on City test rows versus City-specific model evaluated on the same City test rows
- General model evaluated on Resort test rows versus Resort-specific model evaluated on the same Resort test rows

Result terminology must distinguish model scope from evaluation population:

- `scope`: where the model was trained and which modelling strategy it represents
- `evaluation_population`: where the metrics were calculated

Example:

```text
scope = General
evaluation_population = City
```

versus:

```text
scope = City
evaluation_population = City
```

The outer test must not be used iteratively to retune models or change strategy decisions.

## 9. Expected Individual Deliverable

Every member should eventually provide:

- one algorithm-specific notebook
- clear Markdown explanation
- baseline General, City, and Resort experiments
- grouped CV evidence
- tuning experiment
- baseline-versus-tuned comparison
- training-only novelty comparison
- final chosen configuration for their algorithm family
- interpretation
- limitations
- experiment-result records
- Git commits made by that member

Use a consistent notebook naming pattern agreed by the group, but do not prescribe filenames in this handover.

## 10. Branch Ownership

Recommended branch structure:

- Member A: `model/logistic-regression`
- Member B: `model/decision-tree`
- Member C: `model/random-forest`
- Member D: `model/gradient-boosting`

Branch rules:

- each member creates their branch from the approved shared foundation
- members do not edit another member's model implementation
- shared infrastructure changes require group review
- after foundation handover, algorithm-specific commits should come from the responsible member's own Git account

## 11. Peer-Review Checklist

Before an algorithm branch is merged, another member must verify:

- correct approved training data
- no new outer split
- groups used in CV
- preprocessing inside Pipeline
- test data not used during development
- all three scopes implemented
- baseline preserved
- tuning uses grouped CV
- common metric definitions used
- F1 selection rule respected
- results recorded
- no `predictor_group` in model `X`
- notebook is reproducible
- conclusions match evidence
- specialist superiority is not claimed without a valid same-population comparison

## 12. Member Viva Expectations

Each algorithm owner must be able to explain deeply:

- how their algorithm works conceptually
- why it suits this binary-classification problem
- baseline parameters
- tuned hyperparameters
- validation strategy
- metric choice
- why grouped CV is necessary
- why preprocessing is inside the Pipeline
- baseline versus tuned results
- General versus City versus Resort results
- strengths and weaknesses of their algorithm
- their exact contribution

All members must also understand, at a reasonable level:

- the other three algorithms
- overall comparison
- project novelty
- final selection

## 13. Handover Gate

Before a member starts model implementation, confirm:

- [ ] shared Evaluation 2 foundation merged
- [ ] latest main/foundation branch pulled
- [ ] correct personal algorithm assigned
- [ ] personal model branch created
- [ ] `preprocessing.py` unchanged
- [ ] `modeling.py` unchanged
- [ ] Evaluation 2 protocol read
- [ ] outer-test discipline understood
- [ ] algorithm owner understands the required three scopes
- [ ] algorithm owner understands the baseline-before-tuning rule
- [ ] algorithm owner understands contribution evidence requirements
