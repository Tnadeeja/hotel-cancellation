# Progress Evaluation 1 — Project Summary

## 1. Project Problem

Unexpected hotel booking cancellations make occupancy planning, room allocation, operational planning, and revenue planning more difficult. This project aims to estimate cancellation risk before the final reservation outcome is known, using historical hotel reservation data.

The approved project is **AI-Based Hotel Booking Cancellation Risk Prediction Using Data Mining**. The task is binary classification with `is_canceled` as the target.

## 2. Dataset

The project uses the **Hotel Booking Demand Dataset**. The original dataset contains 119,390 records and 32 columns.

- Target: `is_canceled`
- `0`: Not Cancelled
- `1`: Cancelled
- Not Cancelled: 75,166 records
- Cancelled: 44,224 records
- Overall cancelled: 37.04%
- City Hotel: 79,330 records
- Resort Hotel: 40,060 records

The dataset does not contain a unique booking ID. Therefore, identical records cannot be proven to represent accidental duplicates or separate bookings.

## 3. Refined Project Direction / Novelty

The refined investigation is **Hotel-Type-Specific Cancellation Risk Prediction for City Hotel and Resort Hotel**.

Later modelling will compare:

1. A general approach using both hotel types.
2. A City Hotel-specific approach.
3. A Resort Hotel-specific approach.

Existing exploratory analysis shows the following differences:

- City Hotel cancellation rate: 41.73%
- Resort Hotel cancellation rate: 27.76%
- City Hotel median lead time: 74
- Resort Hotel median lead time: 57
- City Hotel mean stay: 2.98 nights
- Resort Hotel mean stay: 4.32 nights
- Repeated-guest proportion: 2.56% for City Hotel and 4.44% for Resort Hotel

These observations justify further investigation, but they do not prove that separate hotel-specific models will perform better.

## 4. Data Quality Findings

### Missing values

- `company`: 112,593 missing values (94.307%)
- `agent`: 16,340 missing values (13.686%)
- `country`: 488 missing values (0.409%)
- `children`: 4 missing values (0.003%)

### Duplicates

- 31,994 extra exact copies
- 40,165 records involved in repeated groups
- 8,171 repeated groups

Because there is no unique booking ID, duplicate-looking records were not automatically removed.

### Unusual records

- 180 records with zero total guests
- 715 records with zero total stay nights
- ADR range: -6.38 to 5400
- 1 record with negative ADR
- 1,959 records with zero ADR

### IQR screening

An IQR screen flagged 64,004 records in at least one screened field. An IQR flag identifies an unusual statistical value; it does not automatically mean that the record is invalid. The flagged records were therefore retained unless another approved rule applied.

## 5. Key EDA Findings

The overall cancellation rate was 37.04%.

Observed descriptive associations included:

- Median lead time: 113 days for Cancelled records and 45 days for Not Cancelled records
- Lead time of 1–7 days: 10.98% cancellation rate
- Lead time of 181–365 days: 55.45% cancellation rate
- Positive previous cancellations: 91.64% cancellation rate
- No positive previous cancellations: 33.91% cancellation rate
- Repeated guests: 14.49% cancellation rate
- Not repeated guests: 37.79% cancellation rate
- Positive previous non-cancelled history: 5.52% cancellation rate
- No previous non-cancelled history: 38.03% cancellation rate
- `Non Refund` deposit type: 99.36% cancellation rate
- `Refundable` deposit type: 22.22% cancellation rate
- Zero special requests: 47.72% cancellation rate
- One special request: 22.02% cancellation rate
- Two special requests: 22.10% cancellation rate

These are descriptive associations in the observed data. They are not causal effects and are not model performance results.

## 6. Leakage Investigation

The following fields were identified as direct leakage because they describe the final reservation outcome:

- `reservation_status`
- `reservation_status_date`

The following fields raise strong temporal concerns because they may reflect later operational events or accumulated changes:

- `assigned_room_type`
- `booking_changes`

The following fields have timing or source limitations that require a realistic assessment-point decision:

- `deposit_type`
- `days_in_waiting_list`
- `adr`

The dataset is a retrospective snapshot. Some booking attributes may reflect modifications made after the original reservation was created. The project excludes clear outcome information, but it cannot guarantee that every retained attribute represents its exact value at the original creation time.

## 7. Final Feature Decisions

The following features are excluded from the primary model:

- `reservation_status`: direct leakage
- `reservation_status_date`: direct leakage
- `assigned_room_type`: strong temporal concern
- `booking_changes`: strong temporal concern
- `company`: extreme missingness and identifier-like sparsity
- `adr`: unresolved source/timing limitation

The following timing-sensitive or identifier-like fields are retained in the primary preparation:

- `deposit_type`
- `days_in_waiting_list`
- `agent` as a categorical identifier

## 8. Row-Level Preprocessing

Duplicate-looking records are retained because no booking ID proves their identity. Full deduplication would change the observed cancellation rate from 37.042% to 27.490%, so it was rejected for the primary modelling population.

Only 180 definite zero-guest rows were removed. The final modelling population contains 119,210 records.

- Zero-stay rows were retained.
- IQR extremes were retained.
- `Undefined` categories were retained.
- The raw dataset was not overwritten or modified.

## 9. Feature Engineering

Five deterministic features were created on the modelling copy:

- `total_stay_nights` = `stays_in_weekend_nights + stays_in_week_nights`  
  Represents the total recorded stay length.

- `total_guests` = `adults + children + babies`  
  Represents the recorded party size. Missing components leave the total missing.

- `family_booking`  
  Equals 1 when children or babies are greater than zero, 0 when both are known zeros, and missing otherwise.

- `previous_booking_total` = `previous_cancellations + previous_bookings_not_canceled`  
  Represents the amount of recorded previous booking history.

- `previous_cancellation_rate` = `previous_cancellations / previous_booking_total` when the total is greater than zero; 0 when there is no history.  
  Missing previous history remains missing.

## 10. Missing Values

Final modelling missing values were handled as follows:

- `children`: 4 missing values, filled using the training median
- `country`: 478 missing values, represented as the `Missing` category
- `agent`: 16,280 missing values, represented as the `Missing` category
- `total_guests`: 4 missing values, filled using the training median
- `family_booking`: 4 missing values, filled using the training median

Learned imputation values are calculated from training data only. This prevents information from the holdout set being used during preprocessing.

## 11. Encoding and Scaling

Numerical predictors use median imputation followed by `StandardScaler`.

Categorical predictors use constant `Missing` imputation followed by `OneHotEncoder(handle_unknown="ignore")`. The `agent` field is treated as a categorical identifier.

- Numerical predictors: 20
- Categorical predictors: 10
- Unencoded predictors: 30
- Transformed features: 564

One-hot encoding increases the number of columns because categorical values are represented by separate indicator columns.

## 12. Train/Test Strategy

The project uses:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

Only the first deterministic split is used as the holdout. This is not model cross-validation yet.

- Modelling records: 119,210
- Training records: 95,375
- Test records: 23,835
- Training cancellation rate: 37.078%
- Test cancellation rate: 37.072%
- All predictor groups: 83,531
- Training groups: 66,831
- Test groups: 16,700
- Group overlap: 0
- Identical predictor overlap: 0

Predictor-profile grouping creates a grouping identifier from the final unencoded predictors only. This keeps identical predictor profiles on the same side of the holdout boundary. The grouping identifier is not used as a model feature and does not represent a confirmed booking identity.

## 13. Hotel-Specific Future Preparation

The same global group-aware split will be reused for later general and hotel-specific modelling.

| Hotel | Train records | Test records |
|---|---:|---:|
| City Hotel | 63,044 | 16,119 |
| Resort Hotel | 32,331 | 7,716 |

Later general and hotel-specific models will reuse the same corresponding holdout bookings. Separate random hotel-specific splits will not be created.

## 14. Leakage Prevention Controls

The Evaluation 1 preparation applies the following controls:

- The target is separated from the predictors.
- Direct leakage and strong temporal-risk fields are excluded.
- Predictor groups are constructed from predictors only.
- Learned preprocessing is fitted on `X_train` only.
- `X_test` is transformed without refitting the preprocessing steps.
- The raw data is never overwritten.

## 15. Evaluation 1 Status

### Complete

- Data understanding
- Data-quality investigation
- Exploratory data analysis
- Leakage audit
- Preprocessing
- Feature engineering
- Train/test preparation

### Not started

- Model development

Classifiers trained: none.

Prediction metrics calculated: none.

The hotel-specific comparison remains a hypothesis for later modelling. No claim is made that hotel-specific models will perform better.
