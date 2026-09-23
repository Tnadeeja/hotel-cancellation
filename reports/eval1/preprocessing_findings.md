# Preprocessing and Feature Engineering Findings

## Starting Dataset

`data/raw/hotel_bookings.csv`: 119,390 rows × 32 columns. Executed with pandas 3.0.3 and sklearn 1.9.0. Raw data remains unchanged. Calculations come from notebook 05 and src/preprocessing.py.

## Row Cleaning

Started with 119,390 rows and 32 columns. Detected 31,994 extra exact full-row copies in 8,171 repeated groups involving 40,165 records. Removed 0 rows merely for duplication. Removed 180 definitive zero-guest rows directly from the raw working copy, leaving 119,210 modelling records, including 645 zero-night records.

No booking ID establishes whether identical records are accidental copies or separate bookings. Their identity is ambiguous. Full-row deduplication is diagnostic only here: it would materially change the target and hotel distributions. Profile grouping preserves frequency information while keeping identical unencoded model inputs on one side of the holdout.

Actual target distribution before/after zero-guest filtering:

| is_canceled | Raw count | Raw percentage | After zero-guest filter count | After zero-guest filter percentage |
| --- | --- | --- | --- | --- |
| Not Cancelled | 75166 | 62.958 | 75011 | 62.923 |
| Cancelled | 44224 | 37.042 | 44199 | 37.077 |

Actual hotel distribution before/after zero-guest filtering:

| hotel | Raw count | Raw percentage | After zero-guest filter count | After zero-guest filter percentage |
| --- | --- | --- | --- | --- |
| City Hotel | 79330 | 66.446 | 79163 | 66.406 |
| Resort Hotel | 40060 | 33.554 | 40047 | 33.594 |

### Why blanket deduplication was rejected

Hypothetical full-raw-row deduplication (not the primary modelling population):

| is_canceled | Raw count | Raw percentage | Hypothetical deduplicated count | Hypothetical deduplicated percentage |
| --- | --- | --- | --- | --- |
| Not Cancelled | 75166 | 62.958 | 63371 | 72.510 |
| Cancelled | 44224 | 37.042 | 24025 | 27.490 |

| hotel | Raw count | Raw percentage | Hypothetical deduplicated count | Hypothetical deduplicated percentage |
| --- | --- | --- | --- | --- |
| City Hotel | 79330 | 66.446 | 53428 | 61.133 |
| Resort Hotel | 40060 | 33.554 | 33968 | 38.867 |

All members of repeated full-row groups have the following observed target distribution:

| is_canceled | Repeated-group rows | Percentage within repeated-group rows |
| --- | --- | --- |
| Not Cancelled | 16714 | 41.613 |
| Cancelled | 23451 | 58.387 |

Unknown guest totals, zero stays, IQR extremes, and Undefined categories have no additional removal rule. A repeated row may still be removed if it independently meets the definitive zero-guest rule.

## Feature Exclusions

| Feature | Reason |
| --- | --- |
| reservation_status | Direct leakage |
| reservation_status_date | Direct leakage |
| assigned_room_type | Strong temporal concern |
| booking_changes | Strong temporal concern |
| company | Extreme missingness / identifier-like sparsity |
| adr | Primary-set source/timing exclusion; sensitivity experiment later |

The six feature exclusions are unchanged. ADR is not direct leakage and remains a possible later sensitivity experiment. Deposit type and waiting duration are retained with timing limitations; agent remains a categorical identifier.

## Missing-Value Strategy

| Feature | Missing modelling rows | Strategy |
| --- | --- | --- |
| children | 4 | Training median |
| country | 478 | Constant Missing category |
| agent | 16280 | Constant Missing category |
| total_guests | 4 | Training median |
| family_booking | 4 | Training median |

Numerical medians come only from X_train. Missing categorical values use neutral Missing, not No Agent. Undefined categories are retained. Entirely missing training columns: 0.

## Feature Engineering

| Feature | Formula / rule | Purpose / missingness |
| --- | --- | --- |
| total_stay_nights | stays_in_weekend_nights + stays_in_week_nights | Planned/recorded total stay; zero is retained |
| total_guests | adults + children + babies | Party size; any missing component leaves the total missing |
| family_booking | 1 if children > 0 or babies > 0; 0 if both are known zeros; otherwise missing | Recorded child/baby presence; not a claim about relationships |
| previous_booking_total | previous_cancellations + previous_bookings_not_canceled | Amount of prior booking history |
| previous_cancellation_rate | previous_cancellations / previous_booking_total when >0; 0.0 when total=0 | Observed prior cancellation share; unknown history stays missing |

All five deterministic features and missing-value semantics are unchanged. Components remain available; no lead-time categories are added. Independent numerical imputation need not preserve arithmetic identities after imputation.

## Encoding and Scaling

Numerical: median SimpleImputer then StandardScaler. Categorical: constant Missing SimpleImputer then OneHotEncoder(handle_unknown='ignore'). There are 20 numerical and 10 categorical predictors and 564 transformed features. Both matrices contain finite values only. Matrices and fitted transformers remain in memory; no processed CSV is saved.

| Partition | Unencoded rows | Unencoded features | Transformed features | Finite / no missing |
| --- | --- | --- | --- | --- |
| Train | 95375 | 30 | 564 | True |
| Test | 23835 | 30 | 564 | True |

## Train/Test Split

First deterministic split from StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42). One fold is test and four are training, producing an approximately 80/20 group-aware stratified holdout. This is not cross-validation modelling, and no alternative fold/seed was selected. Groups hash only final unencoded predictors, with fixed column order and index=False, before learned transformations. Neither the target nor any excluded field enters group creation. The hash is not a model feature.

| Partition | Records | Cancelled | Not Cancelled | Cancelled percentage |
| --- | --- | --- | --- | --- |
| All modelling records | 119210 | 44199 | 75011 | 37.077 |
| Train | 95375 | 35363 | 60012 | 37.078 |
| Test | 23835 | 8836 | 14999 | 37.072 |

Test share is 19.994%; train/test cancellation-rate gap is 0.006 percentage points. Stratification is approximate because groups cannot be split. The fixed split passes the documented two-percentage-point sanity check; this is not an inferential test.

| All predictor groups | Training groups | Test groups | Group overlap | Identical-predictor test rows in train |
| --- | --- | --- | --- | --- |
| 83531 | 66831 | 16700 | 0 | 0 |

Independent complete-row comparison also confirms zero identical unencoded predictor rows across train/test. Split indices are disjoint and reproducible.

## City Hotel / Resort Hotel Split Preparation

| Hotel | Partition | Records | Percentage of partition |
| --- | --- | --- | --- |
| City Hotel | Train | 63044 | 66.101 |
| Resort Hotel | Train | 32331 | 33.899 |
| City Hotel | Test | 16119 | 67.627 |
| Resort Hotel | Test | 7716 | 32.373 |

Both hotels occur in both partitions. Later general and hotel-specific models will reuse these SAME holdout bookings; no independent hotel splits are created.

## Leakage Prevention

The target is separate; all six approved excluded fields are absent from predictors and signatures. The transformer is fitted only with X_train after the split, and X_test uses transform without refitting. Assertions check training medians, category vocabularies, unchanged fitted statistics, and zero profile overlap. Later model validation should preserve predictor groups and refit learned preprocessing within each training fold. No classifier or model metrics were used.

## Remaining Methodological Limitations

Profile separation is not proof of customer-level, time-based, or true reservation-identity independence. Duplicate identity remains ambiguous without booking IDs. The grouping guarantee is for complete unencoded profiles; imputation or unknown-category encoding can make distinct profiles share a transformed representation. Group allocation only approximately preserves class proportions and holdout size. Reproducibility assumes the same input/order and recorded software versions. Retrospective snapshots and deposit/waiting-time availability limitations remain.

## Evaluation 1 Status

Preprocessing and feature engineering are complete under the revised primary policy. Model development has NOT been performed. No classifiers, prediction metrics, resampling, or tuning were used.
