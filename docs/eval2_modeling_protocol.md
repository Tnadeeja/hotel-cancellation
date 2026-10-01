# Evaluation 2 Modeling Protocol

## 1. Project and Evaluation 2 Context

Project:
AI-Based Hotel Booking Cancellation Risk Prediction Using Data Mining

Target:
- `is_canceled`
- `0 = Not Cancelled`
- `1 = Cancelled`

Task:
- Binary classification

Evaluation 2 begins after the completed Evaluation 1 baseline:
- data understanding
- data-quality audit
- exploratory data analysis
- leakage audit
- preprocessing
- feature engineering
- outer train/test holdout preparation

Current status of the repository:
- No classifier has been trained.
- No model metric has been produced.
- No hyperparameter tuning has been performed.
- No model-development result files have been saved.

Evaluation 2 is the next stage and requires:
- at least four suitable machine-learning algorithms
- appropriate validation
- suitable metrics
- systematic model comparison
- experiment recording
- hyperparameter tuning/optimization
- baseline-vs-tuned comparison
- final model selection and justification

This protocol is the common technical rulebook for all four group members during Evaluation 2.

---

## 2. Preserve the Evaluation 1 Baseline

Evaluation 2 must preserve the currently implemented baseline exactly unless a later experiment is explicitly approved and documented as a separate sensitivity test.

Raw dataset:
- 119,390 rows × 32 columns

Primary modelling population:
- 119,210 rows

Row policy currently in force:
- remove only 180 definitive zero-guest records
- retain ambiguous exact duplicate-looking rows
- retain zero-stay rows
- retain IQR screening candidates
- retain source categories such as `Undefined`

Final source exclusions currently enforced by the repository:

Direct leakage:
- `reservation_status`
- `reservation_status_date`

Strong temporal concern:
- `assigned_room_type`
- `booking_changes`

Quality / identifier concern:
- `company`

Primary source / timing exclusion:
- `adr`

Engineered features currently created in the baseline:
- `total_stay_nights`
- `total_guests`
- `family_booking`
- `previous_booking_total`
- `previous_cancellation_rate`

Final predictor schema currently implemented:
- 20 numerical predictors
- 10 categorical predictors
- 30 total unencoded predictors

Important rule:
- Evaluation 2 must not silently change these rules.
- Any future sensitivity experiment must be clearly labelled as such and documented before it is used for model comparison.

---

## 3. Existing Outer Holdout

The final outer holdout already exists and must be preserved.

Current split summary:
- Total modelling rows: 119,210
- Train: 95,375
- Test: 23,835
- Overall cancellation rate: approximately 37.077%
- Train cancellation rate: approximately 37.078%
- Test cancellation rate: approximately 37.072%

Existing grouping:
- predictor groups are built from the final 30 unencoded predictors
- target is excluded from group creation
- excluded/leakage fields are excluded
- source index is excluded
- predictor-group hash is a partition helper only
- it is not a model feature
- it is not a booking ID
- it is not a customer ID

Existing outer split method:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)
```

The first split is used only as one approximately 80/20 outer holdout.

Verified split properties:
- group overlap between outer train/test = 0
- identical complete unencoded predictor-profile overlap = 0

Critical rule:

The outer test set must not be used during:
- algorithm selection
- hyperparameter selection
- tuning-range decisions
- feature-selection decisions
- choosing General vs hotel-specific configurations
- iterative model development

The outer test set is reserved for final evaluation after candidate configurations are frozen.

---

## 4. Why Ordinary Random CV Must Not Be Used

The project intentionally retained ambiguous duplicate-looking rows because there is no unique booking ID. Therefore, ordinary random cross-validation could place identical final predictor profiles into both a training fold and a validation fold.

This breaks the intended evaluation logic because identical predictor profiles can appear in both sides of CV, even when the raw rows are not obviously duplicates from a definitive identity perspective.

Evaluation 2 must preserve the predictor-group principle inside model-development validation.

Use group-aware stratified CV on the outer training set.

Lock the common inner validation strategy as:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)
```

Important notes:
- These are inner model-development folds.
- This is different from the already-fixed outer holdout.
- Groups must come from the final unencoded predictor profiles of the outer training population.
- Group IDs must be supplied to CV/search as `groups`.
- Group IDs must never enter the feature matrix.

Limitation:
- This prevents identical unencoded predictor profiles from crossing folds, but it does not prove customer-level or booking-level independence because the dataset has no customer ID or booking ID.

---

## 5. Preprocessing Inside Cross-Validation

This section is critical.

Evaluation 1 demonstrated an outer training-fitted transformer. However, Evaluation 2 model validation and tuning must fit preprocessing separately inside each inner CV training fold.

All algorithms must therefore be evaluated through a scikit-learn `Pipeline` conceptually structured as:

```python
Pipeline([
    ("preprocessor", build_preprocessor(...)),
    ("classifier", <algorithm>)
])
```

Do not preprocess the complete outer training set once and then run CV on that globally transformed matrix.

Why this matters:
- If training-set medians, scalers, or one-hot vocabularies are learned from all outer training rows before CV, each validation fold can indirectly influence preprocessing.
- That leaks information from validation folds into the model-building process.

Correct inner-CV behavior:
1. For each training fold within CV:
   - fit the imputer
   - fit the scaler
   - fit the encoder
   - fit the classifier
2. For the corresponding validation fold:
   - transform using only statistics learned from that fold's training rows
   - evaluate the model on that transformed validation split

The outer test set must only be used after the chosen configuration is frozen.

---

## 6. Four Algorithm Owners

The project requires at least four suitable machine-learning algorithm families.

Planned algorithm families:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosting / XGBoost family

Important protocol constraints:
- Do not choose final hyperparameter search spaces in this document.
- Do not choose the final model here.
- Do not claim one algorithm is better before evidence.

Algorithm ownership plan:
- Member A: primary ownership of Logistic Regression
- Member B: primary ownership of Decision Tree
- Member C: primary ownership of Random Forest
- Member D: primary ownership of Gradient Boosting / XGBoost family

Each algorithm owner is responsible for:
- algorithm justification
- baseline experiments
- General / City / Resort experiments
- validation results
- hyperparameter tuning
- baseline-vs-tuned comparison
- interpretation
- experiment documentation

This ownership structure does not replace the need for shared understanding.
Every member must understand:
- the overall project
- preprocessing and feature engineering
- validation strategy
- all four algorithm families
- model comparison logic
- the novelty question
- final selection logic

---

## 7. Three Modelling Scopes

Every algorithm must initially be evaluated under three scopes:

A. General
- Training population: all outer-training bookings

B. City-specific
- Training population: City Hotel rows from the outer training set

C. Resort-specific
- Training population: Resort Hotel rows from the outer training set

Current corresponding outer holdout counts:

City:
- Train: 63,044
- Test: 16,119

Resort:
- Train: 32,331
- Test: 7,716

Important rule:
- These subsets are derived from the same existing global outer holdout.
- Do not create independent random City and Resort train/test splits.

---

## 8. Novelty Comparison Rule

The project novelty is:
- General hotel cancellation prediction
- City Hotel-specific cancellation prediction
- Resort Hotel-specific cancellation prediction

The correct evaluation is not to assume hotel-specific models are better.

The fair comparison is:
- General model evaluated on City outer-test rows
- City-specific model evaluated on those same City outer-test rows

and:
- General model evaluated on Resort outer-test rows
- Resort-specific model evaluated on those same Resort outer-test rows

This is required because comparisons across different populations are not evidence that a hotel-specific model is superior.

The purpose is to test the hotel-specific hypothesis fairly, not to force a hotel-specific result.

### 8.1 Training-only novelty comparison before the outer test

The project must compare General vs hotel-specific strategies before touching the outer test set.

This comparison must use only out-of-fold predictions produced from the approved inner grouped CV procedure on the outer training population.

For a frozen General-model configuration:
- obtain out-of-fold predictions for the outer training population using the approved inner `StratifiedGroupKFold` and the full preprocessing + classifier pipeline
- calculate metrics separately for:
  - City Hotel training rows
  - Resort Hotel training rows

For a frozen City-specific configuration:
- obtain grouped-CV out-of-fold predictions on the City Hotel outer-training population
- calculate City metrics

For a frozen Resort-specific configuration:
- obtain grouped-CV out-of-fold predictions on the Resort Hotel outer-training population
- calculate Resort metrics

The training-only novelty comparisons are therefore:
- General OOF metrics on City training rows vs City-specific OOF metrics on City training rows
- General OOF metrics on Resort training rows vs Resort-specific OOF metrics on Resort training rows

Important rules:
- Only out-of-fold predictions may be used for these development comparisons.
- Never use in-sample fitted predictions as validation evidence.
- Grouping must still prevent identical unencoded predictor profiles from crossing the relevant training/validation folds.
- Preprocessing remains inside the pipeline and is refitted within each fold.
- This training-only comparison is used for modelling and strategy decisions before the outer test is inspected.

The final outer-test novelty comparison is a later confirmation:
- General final model on City outer-test rows vs City-specific final model on the same City outer-test rows
- General final model on Resort outer-test rows vs Resort-specific final model on the same Resort outer-test rows

The outer test must not be used iteratively to decide or retune the strategy.

---

## 9. Common Metrics and Scoring Conventions

All algorithms must report the same metrics.

Required metrics:
- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

Confusion Matrix must be reported for final outer-holdout evaluations.

For inner cross-validation, record mean and standard deviation where applicable for:
- Accuracy
- Precision
- Recall
- F1
- ROC-AUC

Primary model-selection metric:
- F1-score

Important secondary metric:
- Recall

Also report:
- Precision
- ROC-AUC
- Accuracy

Important rule:
- F1 is the common primary metric so all group members do not select models using different criteria after seeing results.
- Do not change the decision threshold from the estimator's normal/default classification rule as part of the common baseline protocol.
- Any later threshold optimization must be a separately approved experiment using training/CV information only.

### 9.1 Reproducibility and scoring conventions

- Positive class for binary classification: `1 = Cancelled`
- Use `random_state=42` wherever the estimator, CV splitter, or search procedure supports a random seed, unless a later experiment explicitly documents a different seed.
- Precision, Recall, and F1 must refer to class `1` (Cancelled) as the positive class.
- For scorer implementations where division-by-zero could occur, use a consistent `zero_division=0` policy rather than allowing different behaviour between members.
- ROC-AUC must be computed from continuous model scores: `predict_proba()` probabilities when available, or `decision_function()` scores where appropriate, not from hard 0/1 class predictions.
- Every member must use the same scoring definitions.

---

## 10. Baseline Before Tuning

Every algorithm owner must first produce baseline experiments for:
- General
- City-specific
- Resort-specific

Planned baseline experiment matrix:
- 4 algorithm families × 3 scopes = 12 baseline model instances

Important clarification:
- These are 12 fitted/configured model experiments, not 12 different algorithm families.
- Baseline results must be preserved before hyperparameter tuning begins.

---

## 11. Hyperparameter Tuning Rules

After baseline results are recorded:
- tune suitable hyperparameters
- use an appropriate `GridSearchCV`, `RandomizedSearchCV`, or other justified scikit-learn-compatible search
- use the common inner `StratifiedGroupKFold`
- provide groups to the search fitting procedure
- keep preprocessing inside the pipeline
- use outer-training data only
- never use outer-test results to select hyperparameters
- record the search space
- record best parameters
- record best CV score
- compare tuned CV results against baseline CV results

Important rule:
- Do not define algorithm-specific search spaces in this common protocol.
- Those are the responsibility of each algorithm owner and must be justified.

---

## 12. Test-Set Discipline

Model-development order must be explicit:

1. Outer training data
2. Baseline grouped CV
3. Training-only OOF novelty comparisons
4. Tuning grouped CV
5. Model/configuration decisions
6. Freeze configuration
7. Final fit on the appropriate complete outer-training population
8. Final evaluation on untouched corresponding outer-test rows

### 12.1 Model development / selection

Model development and selection are performed from outer-training data using grouped CV and training-only OOF evidence.

This includes:
- algorithm configuration
- hyperparameter tuning
- General-vs-specialist strategy decisions

### 12.2 Outer test

The outer test is inspected only after candidate configurations and strategy decisions have been frozen.

It is used for final unbiased performance reporting and confirmation only.

It must not trigger repeated retuning or strategy changes while still being described as untouched.

If final test results reveal an important unexpected issue, it may be discussed as a limitation or post-hoc observation, but the test must not silently become another tuning set.

---

## 13. Result Recording

The minimum experiment information every member must record is:
- algorithm
- scope: General / City / Resort
- baseline or tuned
- CV strategy
- random seed where applicable
- parameter configuration
- training row count
- number of predictor groups
- mean CV Accuracy
- std CV Accuracy
- mean CV Precision
- std CV Precision
- mean CV Recall
- std CV Recall
- mean CV F1
- std CV F1
- mean CV ROC-AUC
- std CV ROC-AUC
- tuning method
- best parameters where relevant
- important observation / interpretation

Final outer-test records later additionally include:
- Accuracy
- Precision
- Recall
- F1
- ROC-AUC
- confusion matrix counts

Do not create the CSV/result file yet.
Only document the expected schema.

---

## 14. Contribution Policy

Contribution ownership plan:

Member A:
- primary ownership of Logistic Regression

Member B:
- primary ownership of Decision Tree

Member C:
- primary ownership of Random Forest

Member D:
- primary ownership of Gradient Boosting / XGBoost family

Each owner works on:
- General
- City
- Resort
- baseline
- tuning
- comparison
- interpretation

Common/group work:
- modelling protocol
- validation rules
- metric definitions
- cross-algorithm comparison
- novelty conclusion
- final model/strategy selection

Important rule:
- Algorithm ownership does not mean a student only needs to understand their own algorithm.
- Every member must understand the full project, the preprocessing, the validation strategy, the four model families, the comparison logic, the novelty, and the final selection process.

---

## 15. Prohibited Inconsistencies

Members must not independently:
- create new random train/test splits
- drop duplicate-looking rows
- change the six exclusion fields
- change the five engineered features
- use different preprocessing rules without an approved experiment
- fit preprocessing before CV on the complete outer training set
- use ordinary random CV that ignores predictor groups
- use the outer test set during tuning
- add `predictor_group` as a model feature
- choose a different primary metric for their own model
- claim hotel-specific superiority before final comparison
- overwrite raw data

---

## 16. Intentionally Deferred Decisions

The following decisions are intentionally deferred and must be made later through experiments rather than assumptions:
- exact algorithm hyperparameter search spaces
- whether the fourth algorithm is implemented with scikit-learn `GradientBoostingClassifier` or XGBoost
- final tuned configurations
- final algorithm/model strategy
- whether General or hotel-specific modelling performs better
- any feature-selection or sensitivity experiment
- any probability-threshold optimization
- final system deployment model(s)

---

## 17. Final Protocol Statement

This document is the common Evaluation 2 rulebook for the project.

It preserves the verified Evaluation 1 baseline and explicitly separates:
- the fixed outer holdout
- the inner group-aware CV procedure used for model development
- the training-only OOF evidence used to compare modelling strategies
- the final outer-test evaluation only after model selection is frozen

It emphasizes the fact that the repository currently stops at preprocessing and holdout preparation and that no model has yet been trained.

The purpose of Evaluation 2 is to compare models scientifically under the current preprocessing and split policy, not to change those rules under the hood.
