# Preprocessing Policy

## Principles

Raw data is immutable. All row rules, exclusions, and deterministic feature engineering operate on copies through `src/preprocessing.py`. The target is separated before splitting or fitting. Learned transformations use X_train only. No prediction model is trained in Evaluation 1.

The preceding leakage audit records classification/review status at that stage. This policy resolves the authorised primary-set preprocessing choices without changing those leakage-risk distinctions.

## Row-Level Decisions

Detect exact duplicate copies and repeated groups, but retain duplicate-looking rows in the PRIMARY dataset. Without a unique booking ID their identity is ambiguous: they are neither proven accidental copies nor proven separate reservations. The notebook reports hypothetical deduplication distributions as supporting evidence only; blanket removal would materially change target and hotel proportions. No drop_duplicates call occurs in the primary pipeline.

Remove ONLY definitively zero totals from adults + children + babies, directly from the complete raw working copy. Missing components leave an unknown total and do not trigger removal. Preserve source indices and all remaining row frequencies. Keep zero-stay observations unless they independently meet the zero-guest rule; do not cap/filter IQR extremes or change Undefined categories.

Full-row deduplication and profile separation are different tasks: records can differ in subsequently excluded fields but become identical predictors. Protect the holdout boundary using predictor-profile groups, not blanket deletion of ambiguous reservations.

## Feature Exclusions

### Direct Leakage

`reservation_status`, `reservation_status_date`: final outcome information.

### Strong Temporal Concern

`assigned_room_type`, `booking_changes`: later allocation and accumulated amendments.

### Data Quality / Feature Selection

`company`: extreme missingness and identifier-like sparsity. This is not a leakage decision.

### Primary-Model Source/Timing Exclusion

`adr`: unresolved source/timing limitation and unusual recorded extremes. Not direct target leakage. ADR may be revisited in a sensitivity/alternative-feature experiment during model development; the raw values remain intact.

## Missing Values

Numerical fields use `SimpleImputer(strategy="median")` fitted on X_train only. In the current working data this affects children, total_guests, and family_booking. Categorical missing values, currently in agent and country, use `SimpleImputer(strategy="constant", fill_value="Missing")`. No full-data imputation occurs.

Categorical null representation is normalised to numpy NaN for sklearn interoperability, without supplying values. Both imputers preserve empty feature columns; the notebook checks that no current training column is entirely missing. If a future numerical training column is entirely missing, the library's zero fallback requires review rather than being interpreted as a learned median.

## Categorical Variables

Agent codes are converted to strings, with integral numeric values such as 9.0 becoming "9". Missing agent values remain missing until the pipeline and are not assumed to mean No Agent. Hotel remains categorical for the global pipeline. Retain Undefined source categories. OneHotEncoder(handle_unknown="ignore") learns categories on training data; unseen categories receive all-zero indicators for that field.

Retain deposit_type as a categorical candidate with its timing/source limitation documented. It is not direct leakage.

## Numerical Variables

Use training-fitted median imputation followed by StandardScaler. Retain days_in_waiting_list with assessment-point-dependent availability. Numerical count/date components and the engineered family indicator use this branch as specified. No lead-time binning is applied. Scaling is not an outlier filter.

Numerical features: `lead_time`, `arrival_date_year`, `arrival_date_week_number`, `arrival_date_day_of_month`, `stays_in_weekend_nights`, `stays_in_week_nights`, `adults`, `children`, `babies`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`, `days_in_waiting_list`, `required_car_parking_spaces`, `total_of_special_requests`, `total_stay_nights`, `total_guests`, `family_booking`, `previous_booking_total`, `previous_cancellation_rate`.

Categorical features: `hotel`, `arrival_date_month`, `meal`, `country`, `market_segment`, `distribution_channel`, `reserved_room_type`, `deposit_type`, `agent`, `customer_type`.

## Feature Engineering

| Feature | Formula / rule | Purpose / missingness |
| --- | --- | --- |
| total_stay_nights | stays_in_weekend_nights + stays_in_week_nights | Planned/recorded total stay; zero is retained |
| total_guests | adults + children + babies | Party size; any missing component leaves the total missing |
| family_booking | 1 if children > 0 or babies > 0; 0 if both are known zeros; otherwise missing | Recorded child/baby presence; not a claim about relationships |
| previous_booking_total | previous_cancellations + previous_bookings_not_canceled | Amount of prior booking history |
| previous_cancellation_rate | previous_cancellations / previous_booking_total when >0; 0.0 when total=0 | Observed prior cancellation share; unknown history stays missing |

These operations are deterministic and learn no statistics. Component features remain available. Missing inputs propagate to totals; a positive child/baby count is sufficient for family_booking=1 even if the other is missing. Both must be known zeros for family_booking=0. Missing previous history stays missing. The no-history cancellation rate is explicitly 0.0.

Independent median imputation of components and their engineered totals may not preserve exact arithmetic identities in imputed rows. This follows the requested pipeline and is a representation choice to revisit during later model development if needed.

## Train/Test Strategy

Use the first deterministic split from StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42). One fold is test and the other four are training: approximately an 80/20 holdout. This is partition preparation only, not cross-validation modelling; no alternative fold or seed is selected.

Create group IDs from final unencoded predictors after deterministic engineering and approved feature exclusions, before any learned transformation. The reusable create_predictor_groups(X) validates the exact predictor schema, fixes column order, and uses pd.util.hash_pandas_object(..., index=False). It excludes the target, all six excluded fields, and source row indices. The signature is NOT a model feature. The target is used for stratification, never signature construction. A rare hash collision conservatively co-groups profiles; independent complete-row checks protect the boundary.

Assert disjoint train/test source indices and group IDs, zero identical complete predictor rows crossing the boundary, both hotel types in both sets, and repeatability with the same input/order and software versions. Report actual split fractions and cancellation rates. Use a two-percentage-point train/test rate-gap sanity check, not an inferential test or reason to search other folds. If profile overlap is nonzero, stop rather than hiding it.

Build an unfitted ColumnTransformer after splitting. Only fit_transform(X_train) learns medians, scaling and one-hot categories; X_test uses transform without refitting. Future model validation should preserve groups and refit preprocessing inside each training fold. No processed CSV, encoded/scaled matrix, or fitted model artifact is saved.

## Hotel-Specific Modelling Preparation

Use City/Resort subsets of the SAME global group-aware train/test partition. Train hotel-specific models later on corresponding training subsets and compare against the general model on the identical hotel-specific holdout bookings. Do not generate separate random hotel splits. Removing constant hotel within a hotel-specific model is deferred to that stage.

## Remaining Limitations

- Duplicate-looking rows are retained because booking identity is unknown. Profile grouping prevents identical unencoded model inputs on both sides of the holdout but does not prove customer-level or reservation-identity independence.
- Distinct unencoded profiles may converge after imputation or unknown-category encoding; the asserted separation is defined on complete unencoded predictors as specified.
- Groups have unequal sizes and may contain mixed outcomes. Stratification and the 80/20 row ratio are approximate. This is not a temporal holdout.
- The source is retrospective and does not guarantee original creation-time values; updated booking details are not automatically leakage.
- Deposit type remains sensitive to payment timing; waiting duration is known after confirmation. Retention needs a realistic pre-outcome assessment point.
- ADR remains excluded from the primary set for source/timing reasons; sensitivity experiments remain future work.
