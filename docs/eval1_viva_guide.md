# Progress Evaluation 1 — Viva Preparation Guide

This guide helps explain the project in simple but technically correct language during an individual viva.

## A. Project Basics

### 1. What is your project?

**Short viva answer**

My project is **AI-Based Hotel Booking Cancellation Risk Prediction Using Data Mining**. It is a binary classification investigation using hotel booking data.

**If lecturer asks deeper**

The refined investigation compares cancellation-risk modelling for City Hotel and Resort Hotel, but the comparison will happen during later model development.

**Common mistake to avoid**

Do not say that a classifier has already been built.

### 2. What problem are you solving?

**Short viva answer**

I am trying to estimate whether a booking is likely to be cancelled before the final reservation outcome is known.

**If lecturer asks deeper**

Unexpected cancellations make occupancy planning, room allocation, operational planning, and revenue planning more difficult.

### 3. Why is it a classification problem?

**Short viva answer**

It is classification because the outcome belongs to one of two classes: cancelled or not cancelled.

**If lecturer asks deeper**

The project may later produce a class prediction or a cancellation-risk probability, but no prediction model has been trained yet.

### 4. What is the target?

**Short viva answer**

The target is `is_canceled`.

**If lecturer asks deeper**

The value 0 means Not Cancelled and the value 1 means Cancelled.

### 5. Who are the intended stakeholders?

**Short viva answer**

The intended stakeholders are hotel managers and teams responsible for occupancy, room allocation, operations, and revenue planning.

**If lecturer asks deeper**

A future risk estimate could help them identify bookings that may need closer planning attention, subject to model validation.

### 6. What is your project novelty?

**Short viva answer**

The refined direction is Hotel-Type-Specific Cancellation Risk Prediction for City Hotel and Resort Hotel.

**If lecturer asks deeper**

The planned comparison is between a general approach, a City Hotel-specific approach, and a Resort Hotel-specific approach.

**Common mistake to avoid**

Booking-time prediction is not being claimed as the novelty, and the comparison is not yet a result.

### 7. Why compare City Hotel and Resort Hotel?

**Short viva answer**

The exploratory analysis shows different observed cancellation rates and booking patterns for the two hotel types.

**If lecturer asks deeper**

City cancellation was 41.73% and Resort cancellation was 27.76%. Their lead-time, stay-length, and repeated-guest patterns also differed.

### 8. Have you proved hotel-specific models are better?

**Short viva answer**

No. That is a hypothesis for later modelling, not an established finding.

**If lecturer asks deeper**

The models must be trained and compared on the same corresponding holdout bookings before making that claim.

## B. Dataset Understanding

### 9. Which dataset is used?

**Short viva answer**

I use the Hotel Booking Demand Dataset.

**If lecturer asks deeper**

The local source file is `data/raw/hotel_bookings.csv`.

### 10. How many rows and columns are in the raw dataset?

**Short viva answer**

The raw dataset has 119,390 rows and 32 columns.

**If lecturer asks deeper**

The 32 columns include the target and outcome-related fields, not just the final predictors.

### 11. What does one row represent?

**Short viva answer**

One row represents one recorded hotel booking.

**If lecturer asks deeper**

The row contains reservation attributes, customer-history information, and the recorded cancellation outcome.

### 12. What are numerical and categorical features?

**Short viva answer**

Numerical features contain quantities or numeric measurements. Categorical features contain labels or codes representing groups.

**If lecturer asks deeper**

The final preprocessing uses 20 numerical predictors and 10 categorical predictors.

### 13. Why can a numeric dtype still be categorical?

**Short viva answer**

A number can be a code rather than a measurement. Its pandas dtype does not automatically determine its modelling meaning.

**If lecturer asks deeper**

The `agent` field is numeric in the raw file, but it is treated as a categorical identifier and converted to string codes.

### 14. What is class imbalance?

**Short viva answer**

Class imbalance means that the target classes do not have equal numbers of records.

**If lecturer asks deeper**

There are 75,166 Not Cancelled records and 44,224 Cancelled records.

### 15. Is this dataset severely imbalanced?

**Short viva answer**

No. The classes are not equal, but 37.04% of bookings are cancelled, so this is not an extreme imbalance.

**If lecturer asks deeper**

The class distribution should still be monitored when evaluating models, but the project does not claim that balancing is required.

### 16. Did you apply SMOTE or balancing?

**Short viva answer**

No. No resampling or balancing was applied in Evaluation 1.

**If lecturer asks deeper**

The project first prepares a leakage-controlled holdout. Any later resampling decision would need to be justified using the training data only.

## C. Data Quality

### 17. Which columns have missing values?

**Short viva answer**

The main missing-value findings were `company`, `agent`, `country`, and `children`.

**If lecturer asks deeper**

`company` has 112,593 missing values, `agent` has 16,340, `country` has 488, and `children` has 4.

### 18. What are the missing-value percentages?

**Short viva answer**

The percentages are 94.307% for `company`, 13.686% for `agent`, 0.409% for `country`, and 0.003% for `children`.

**If lecturer asks deeper**

Missingness does not automatically mean that a record is incorrect. The treatment depends on the field's meaning and modelling role.

### 19. Why is `company` treated differently from `agent`?

**Short viva answer**

`company` has extreme missingness and identifier-like sparsity, so it is excluded from the primary model. `agent` is retained as a categorical identifier.

**If lecturer asks deeper**

`company` has 94.307% missing values, while `agent` has 13.686%. This is a data-quality and feature-selection decision, not a leakage decision.

### 20. Why not drop every row with missing values?

**Short viva answer**

Dropping every incomplete row would remove many observations and could change the data distribution unnecessarily.

**If lecturer asks deeper**

The project uses training-fitted numerical imputation and a neutral `Missing` category for categorical fields instead.

### 21. How many duplicates were found?

**Short viva answer**

There were 31,994 extra exact copies, 40,165 rows involved in repeated groups, and 8,171 repeated groups.

**If lecturer asks deeper**

There were 87,396 distinct full-row patterns, and some identical rows occurred many times.

### 22. Why were duplicate-looking rows not removed?

**Short viva answer**

There is no unique booking ID, so identical rows cannot be proven to be accidental duplicates.

**If lecturer asks deeper**

They could represent repeated valid bookings or duplicated records. Removing them would also change booking frequencies and the target distribution.

**Common mistake to avoid**

Do not call them definitely valid bookings or definitely data-entry errors.

### 23. What would full deduplication change?

**Short viva answer**

The observed cancellation rate would change from 37.042% to 27.490% in the hypothetical deduplicated data.

**If lecturer asks deeper**

That material change was one reason full deduplication was not used for the primary modelling population.

### 24. Why were zero-guest rows removed?

**Short viva answer**

A row with known adults, children, and babies summing to zero is definitively inconsistent with a booking containing guests.

**If lecturer asks deeper**

Only 180 definite zero-guest rows were removed. Missing guest components were not treated as zero.

### 25. Why were zero-stay rows retained?

**Short viva answer**

A zero-stay record is unusual, but it was not automatically proven invalid by the existing evidence.

**If lecturer asks deeper**

There were 715 raw zero-stay records. The policy retains them unless they independently satisfy the zero-guest rule.

### 26. What is an outlier?

**Short viva answer**

An outlier is an observation that is unusually far from the general pattern of a variable.

**If lecturer asks deeper**

Unusual values may be valid cases, data problems, or values needing context, so an outlier flag alone is not enough to remove a record.

### 27. What is IQR?

**Short viva answer**

IQR is the interquartile range: the third quartile minus the first quartile.

**If lecturer asks deeper**

The audit used a 1.5 times IQR rule to screen selected numerical fields.

### 28. Why were IQR outliers not automatically removed?

**Short viva answer**

An IQR flag indicates statistical unusualness, not automatic invalidity.

**If lecturer asks deeper**

The screen flagged 64,004 records in at least one screened field, and many count fields had zero IQR. Removing all of them would be unjustified.

### 29. What happened to `Undefined` categories?

**Short viva answer**

They were retained because they are observed source categories, not automatically invalid values.

**If lecturer asks deeper**

Their meaning can be reviewed later, but the current policy does not silently recode or remove them.

### 30. What unusual ADR values were found?

**Short viva answer**

ADR ranged from -6.38 to 5400. There was 1 negative value and 1,959 zero values.

**If lecturer asks deeper**

ADR was excluded from the primary model because of unresolved source and timing limitations, not because it was direct target leakage.

## D. Exploratory Data Analysis

### 31. What is EDA?

**Short viva answer**

EDA is exploratory data analysis: examining distributions, patterns, missingness, and relationships before modelling.

**If lecturer asks deeper**

It helps understand the data and identify quality or leakage questions without claiming predictive performance.

### 32. Why perform EDA before preprocessing?

**Short viva answer**

EDA helps make informed preprocessing decisions instead of changing values blindly.

**If lecturer asks deeper**

For example, it showed differences between hotel types and identified unusual guest totals, stay lengths, ADR values, and cancellation patterns.

### 33. What did the City versus Resort comparison show?

**Short viva answer**

City Hotel had a 41.73% cancellation rate, while Resort Hotel had a 27.76% rate.

**If lecturer asks deeper**

City had median lead time 74 and mean stay 2.98 nights. Resort had median lead time 57 and mean stay 4.32 nights. Repeated-guest proportions were 2.56% and 4.44% respectively.

### 34. What did lead time show?

**Short viva answer**

Cancelled bookings had a median lead time of 113 days, while Not Cancelled bookings had a median of 45 days.

**If lecturer asks deeper**

Bookings with 1-7 days had a 10.98% cancellation rate, while bookings with 181-365 days had a 55.45% rate.

### 35. What did previous cancellations show?

**Short viva answer**

Bookings with positive previous cancellations had a 91.64% observed cancellation rate, compared with 33.91% when there were no positive previous cancellations.

**If lecturer asks deeper**

This is based on recorded previous customer history and is an association, not a causal conclusion.

### 36. What did repeated guests show?

**Short viva answer**

Repeated guests had a 14.49% cancellation rate, while guests not recorded as repeated had a 37.79% rate.

**If lecturer asks deeper**

The repeated-guest indicator is treated as prior customer history and is not considered direct leakage.

### 37. What did previous non-cancelled bookings show?

**Short viva answer**

Bookings with positive previous non-cancelled history had a 5.52% cancellation rate, while those with no positive history had a 38.03% rate.

**If lecturer asks deeper**

This is another descriptive comparison of recorded prior history.

### 38. What did deposit type show?

**Short viva answer**

`Non Refund` bookings had a 99.36% cancellation rate, while `Refundable` bookings had a 22.22% rate.

**If lecturer asks deeper**

`deposit_type` is retained but its timing relative to the prediction point needs to be considered.

### 39. What did special requests show?

**Short viva answer**

The observed cancellation rates were 47.72% for zero requests, 22.02% for one request, and 22.10% for two requests.

**If lecturer asks deeper**

These are unadjusted group rates and are not model results.

### 40. Can these relationships be called causal?

**Short viva answer**

No. They are descriptive associations in the observed data.

**If lecturer asks deeper**

The EDA does not control for all other variables, establish time order for every field, or conduct an experimental design.

### 41. What is the difference between association and causation?

**Short viva answer**

Association means two observed patterns occur together. Causation means a change in one factor produces a change in another, which these summaries do not prove.

**Common mistake to avoid**

Do not say that a long lead time, deposit type, or previous history causes cancellation based only on these tables.

## E. Data Leakage

### 42. What is data leakage?

**Short viva answer**

Data leakage happens when information unavailable at prediction time, especially information about the outcome, enters the predictors.

**If lecturer asks deeper**

Leakage can make evaluation look unrealistically strong because the model receives information from after or too close to the outcome.

### 43. Why is `reservation_status` leakage?

**Short viva answer**

It records the final reservation status, so it directly describes the outcome being predicted.

**If lecturer asks deeper**

The observed cross-tab shows `Canceled` has target 0 equal to 0 and target 1 equal to 43,017; `Check-Out` has target 0 equal to 75,166 and target 1 equal to 0.

### 44. What evidence supports excluding `reservation_status`?

**Short viva answer**

Its values correspond directly to final outcomes in the observed data.

**If lecturer asks deeper**

`No-Show` also has target 0 equal to 0 and target 1 equal to 1,207. This makes the field outcome-related rather than a legitimate pre-outcome predictor.

### 45. Why is `reservation_status_date` leakage?

**Short viva answer**

It is the date associated with the final reservation status, so it contains final-outcome event information.

**If lecturer asks deeper**

It is excluded because of its outcome-event meaning, not because every individual date necessarily determines the target by itself.

### 46. Why exclude `assigned_room_type`?

**Short viva answer**

It describes the ultimate room assignment and may reflect later operations or customer changes.

**If lecturer asks deeper**

It is a strong temporal concern and is different from `reserved_room_type`, which records the requested room type.

### 47. Why exclude `booking_changes`?

**Short viva answer**

It accumulates amendments over time and may include events occurring after the intended assessment point.

**If lecturer asks deeper**

The audit found 18,076 positive counts, so it can summarize later booking activity rather than only initial reservation information.

### 48. Why is `previous_cancellations` not leakage?

**Short viva answer**

It describes prior customer history, not the final outcome of the current booking.

**If lecturer asks deeper**

The audit treats it as a candidate predictor under the assumption that the history predates the current booking outcome.

### 49. Is `deposit_type` leakage?

**Short viva answer**

It is not classified as direct leakage, but its timing relative to the prediction point needs review.

**If lecturer asks deeper**

It may reflect payments made before arrival or cancellation, so availability depends on when the risk estimate is meant to be made.

### 50. What about `days_in_waiting_list`?

**Short viva answer**

It has a timing limitation because waiting duration may be known only after confirmation.

**If lecturer asks deeper**

It is retained in the primary preparation, but its suitability depends on the realistic operational assessment point.

### 51. Why is ADR excluded even though it is not direct leakage?

**Short viva answer**

ADR is excluded because its source and timing at the intended prediction point are unresolved.

**If lecturer asks deeper**

It is a primary-model source/timing exclusion, not a direct target-leakage exclusion. A later sensitivity experiment could revisit it.

### 52. What is the retrospective snapshot limitation?

**Short viva answer**

The dataset is a retrospective snapshot, so some booking values may reflect changes made after the original reservation was created.

**If lecturer asks deeper**

The project excludes clear outcome information, but it cannot guarantee that every retained value exactly represents the value available at booking creation.

## F. Feature Engineering

### 53. What is feature engineering?

**Short viva answer**

Feature engineering creates useful representations from existing columns without changing the raw dataset.

**If lecturer asks deeper**

The five engineered features are deterministic calculations performed on a modelling copy.

### 54. Why create `total_stay_nights`?

**Short viva answer**

It combines weekend and weekday nights into one total stay-length measure.

**If lecturer asks deeper**

The formula is `stays_in_weekend_nights + stays_in_week_nights`.

### 55. Why create `total_guests`?

**Short viva answer**

It gives one recorded party-size measure by adding adults, children, and babies.

**If lecturer asks deeper**

The formula is `adults + children + babies`. If a component is missing, the total remains missing until the training pipeline imputes it.

### 56. What is `family_booking`?

**Short viva answer**

It is 1 when children or babies are greater than zero, 0 when both are known zeros, and missing otherwise.

**If lecturer asks deeper**

It indicates recorded child or baby presence; it is not a claim about family relationships.

### 57. Why create `previous_booking_total`?

**Short viva answer**

It combines previous cancellations and previous non-cancelled bookings into one measure of prior booking history.

**If lecturer asks deeper**

The formula is `previous_cancellations + previous_bookings_not_canceled`.

### 58. Why create `previous_cancellation_rate`?

**Short viva answer**

It represents the share of the recorded previous booking history that was cancelled.

**If lecturer asks deeper**

It is previous cancellations divided by total previous bookings when the total is greater than zero, and 0 when there is no previous history.

### 59. Why did you not add a lead-time category?

**Short viva answer**

No lead-time category was approved in the current preprocessing policy.

**If lecturer asks deeper**

The raw numerical lead time is retained. Later model development can compare representations if there is a justified reason.

## G. Missing Values, Encoding, and Scaling

### 60. What is imputation?

**Short viva answer**

Imputation replaces missing values with a defined value or category so the modelling pipeline can process them.

**If lecturer asks deeper**

The numerical pipeline uses a median, while the categorical pipeline uses a `Missing` category.

### 61. Why use the median instead of the mean?

**Short viva answer**

The median is less affected by extreme values and skewed distributions than the mean.

**If lecturer asks deeper**

The project uses the training median as a robust summary for numerical missing values.

### 62. Why fit imputation on training data only?

**Short viva answer**

The test set must not influence the learned preprocessing values.

**If lecturer asks deeper**

Using training data only prevents information from the holdout from entering the preparation process.

### 63. How are categorical missing values handled?

**Short viva answer**

They are represented by a constant `Missing` category.

**If lecturer asks deeper**

After filtering, `country` has 478 missing modelling values and `agent` has 16,280. Missing agent is not assumed to mean no agent.

### 64. Why use `OneHotEncoder`?

**Short viva answer**

One-hot encoding converts categorical values into numerical indicator columns that a model can use.

**If lecturer asks deeper**

Each learned category can receive its own column, while the original categorical meaning is not treated as an artificial numeric order.

### 65. What does `handle_unknown="ignore"` mean?

**Short viva answer**

If a category appears in test data but was not seen during training, the encoder does not fail.

**If lecturer asks deeper**

That unseen category receives no learned indicator for that field rather than changing the training vocabulary.

### 66. Why is `agent` categorical?

**Short viva answer**

Agent values are codes or identifiers, not measurements where a larger number has a meaningful size.

**If lecturer asks deeper**

The implementation converts integral numeric codes such as 9.0 to string categories before encoding.

### 67. What does `StandardScaler` do?

**Short viva answer**

It standardizes numerical features using statistics learned from the training data.

**If lecturer asks deeper**

It puts numerical variables on comparable scales; it is not an outlier-removal method.

### 68. Do all algorithms require scaling?

**Short viva answer**

No. Scaling is especially important for algorithms affected by feature magnitude, but some tree-based methods are less sensitive to it.

**If lecturer asks deeper**

The project defines one consistent numerical preprocessing branch before model development.

### 69. Why are there 564 transformed features?

**Short viva answer**

The 30 unencoded predictors expand after categorical values are one-hot encoded, while the numerical features remain numerical columns.

**If lecturer asks deeper**

There are 20 numerical predictors and 10 categorical predictors before transformation, producing 564 transformed columns for the fitted training vocabulary.

## H. Train/Test Split

### 70. Why split the data?

**Short viva answer**

A split provides training data for learning and holdout data for later evaluation on records not used to fit the model.

**If lecturer asks deeper**

The split also gives a boundary for fitting preprocessing only on training predictors.

### 71. What are the training and test sets?

**Short viva answer**

The training set is used to learn preprocessing and later model parameters. The test set is held out for evaluation.

**If lecturer asks deeper**

At Evaluation 1, the test set is a prepared holdout, not an external prospective evaluation.

### 72. Why use approximately 80/20?

**Short viva answer**

It provides enough data for training while reserving a meaningful holdout for evaluation.

**If lecturer asks deeper**

The actual split has 95,375 training records and 23,835 test records, or approximately 80/20.

### 73. What is stratification?

**Short viva answer**

Stratification tries to keep the target class proportions similar across the partitions.

**If lecturer asks deeper**

The train cancellation rate is 37.078% and the test cancellation rate is 37.072%.

### 74. Why not use ordinary `train_test_split`?

**Short viva answer**

Ordinary random splitting does not provide the same group-aware protection against identical predictor profiles crossing the boundary.

**If lecturer asks deeper**

The project uses stratification and grouping together because duplicate identity is uncertain and predictor profiles can repeat.

### 75. What is a predictor profile?

**Short viva answer**

A predictor profile is the complete set of final unencoded predictor values for one record.

**If lecturer asks deeper**

It excludes the target, the six approved excluded fields, and the source row index.

### 76. Why group identical predictor profiles?

**Short viva answer**

Identical profiles should not appear in both training and test partitions because that would weaken the holdout separation.

**If lecturer asks deeper**

Grouping preserves repeated-row frequency while preventing identical final unencoded inputs from crossing the boundary.

### 77. How are groups created?

**Short viva answer**

The final unencoded predictors are placed in a fixed column order and hashed with `pd.util.hash_pandas_object` using `index=False`.

**If lecturer asks deeper**

The target and excluded fields do not enter the hash. The hash is a deterministic grouping identifier only.

### 78. Is the hash a model feature?

**Short viva answer**

No. It is used only to form groups for the split.

**If lecturer asks deeper**

Treating the hash as a model feature would turn a partition-control identifier into an artificial predictor.

### 79. What is `StratifiedGroupKFold` doing here?

**Short viva answer**

It creates folds while considering both target proportions and group membership.

**If lecturer asks deeper**

The project uses `n_splits=5`, `shuffle=True`, and `random_state=42`, then uses only the first split as the holdout.

### 80. Are you already doing model cross-validation?

**Short viva answer**

No. At Evaluation 1, this is only being used to create one deterministic holdout partition.

**If lecturer asks deeper**

No classifier is fitted across multiple validation folds yet.

### 81. Why is zero group overlap important?

**Short viva answer**

Zero overlap means no predictor group is assigned to both training and test sets.

**If lecturer asks deeper**

There are 83,531 total predictor groups, 66,831 training groups, and 16,700 test groups, with group overlap equal to 0.

### 82. What limitation remains without booking or customer IDs?

**Short viva answer**

The project cannot prove that records belong to different real bookings or different customers.

**If lecturer asks deeper**

Grouping protects identical unencoded predictor profiles, but it does not establish customer-level, booking-identity, or temporal independence.

### 83. How will general and hotel-specific models be compared fairly?

**Short viva answer**

They will reuse the same corresponding holdout bookings from the global group-aware split.

**If lecturer asks deeper**

The City and Resort subsets will be compared without creating separate random hotel-specific splits.

## I. Preprocessing Pipeline

### 84. What is a preprocessing pipeline?

**Short viva answer**

It is an ordered sequence of transformations applied consistently to the predictors.

**If lecturer asks deeper**

Here it includes imputation, scaling for numerical fields, and imputation plus one-hot encoding for categorical fields.

### 85. What is `ColumnTransformer`?

**Short viva answer**

`ColumnTransformer` applies different transformation pipelines to different groups of columns.

**If lecturer asks deeper**

The numerical branch uses median imputation and scaling, while the categorical branch uses `Missing` imputation and one-hot encoding.

### 86. What happens to numerical features?

**Short viva answer**

They receive training-fitted median imputation followed by `StandardScaler`.

**If lecturer asks deeper**

The numerical branch includes the original retained numerical predictors and the five engineered numerical features.

### 87. What happens to categorical features?

**Short viva answer**

They receive constant `Missing` imputation followed by `OneHotEncoder(handle_unknown="ignore")`.

**If lecturer asks deeper**

`hotel`, `agent`, and the other categorical fields are treated according to their semantic roles, not just their raw dtypes.

### 88. When is the transformer fitted?

**Short viva answer**

It is fitted after the split using `X_train` only.

**If lecturer asks deeper**

The training fit learns numerical medians, scaling statistics, and the categorical vocabulary.

### 89. What happens to `X_test`?

**Short viva answer**

`X_test` is transformed using the already fitted transformer.

**If lecturer asks deeper**

It is not used to refit medians, scaling values, or categories.

### 90. Why cannot preprocessing fit on the whole dataset?

**Short viva answer**

Fitting on the whole dataset would allow holdout information to influence the transformation.

**If lecturer asks deeper**

That would create preprocessing leakage, even if no classifier had yet been trained.

### 91. Did you save a processed CSV?

**Short viva answer**

No. No processed CSV, encoded matrix, or fitted model artifact was saved.

**If lecturer asks deeper**

The matrices and transformer were kept in memory for validation, while the raw dataset remained unchanged.

### 92. Why not save a processed CSV?

**Short viva answer**

The project is still at preparation stage, and saving one processed matrix could hide the training-only fitting boundary.

**If lecturer asks deeper**

The reusable code and notebook reproduce the transformations while preserving the raw source.

### 93. What is the role of `preprocessing.py`?

**Short viva answer**

It contains reusable deterministic preparation and train-fitted preprocessing functions.

**If lecturer asks deeper**

It performs row cleaning, feature engineering, feature exclusions, agent conversion, target/predictor separation, predictor grouping, and creation of an unfitted `ColumnTransformer`.

### 94. What does Notebook 05 do?

**Short viva answer**

Notebook 05 performs the split, fits the transformer on `X_train`, transforms `X_test`, and checks the preparation.

**If lecturer asks deeper**

It validates group separation, predictor overlap, transformation results, and the absence of classifier training.

## J. GitHub and Professional Workflow

### 95. Why use GitHub?

**Short viva answer**

GitHub provides version control, collaboration, and a clear history of the project files.

**If lecturer asks deeper**

It also helps separate raw data, reusable source code, notebooks, reports, and documentation in an organized repository.

### 96. Why use branches?

**Short viva answer**

Branches allow a piece of work to be developed separately from other project work.

**If lecturer asks deeper**

The current branch is `docs/eval1-preparation`, which contains the Evaluation 1 preparation work.

### 97. Why preserve raw data?

**Short viva answer**

Keeping the raw data unchanged makes the analysis reproducible and protects the original evidence.

**If lecturer asks deeper**

Cleaning and feature engineering operate on copies, while the raw CSV remains the source reference.

### 98. Why use notebooks plus reusable source code?

**Short viva answer**

Notebooks make the investigation visible, while source code makes the important preparation steps reusable and consistent.

**If lecturer asks deeper**

`preprocessing.py` avoids hiding the final row rules and transformations inside notebook-only cells.

### 99. How should you explain your own contribution?

**Short viva answer**

I should explain the decisions I made, the evidence supporting them, and how I validated the implementation.

**If lecturer asks deeper**

I should be able to explain the data audit, leakage policy, deterministic features, training-only preprocessing, and group-aware holdout without claiming results that were not produced.

## K. Limitations

### 100. Why is the absence of a booking ID a limitation?

**Short viva answer**

Without a booking ID, I cannot determine whether identical rows are duplicates or separate bookings.

**If lecturer asks deeper**

That is why duplicate-looking rows are retained and predictor-profile grouping is used for holdout separation.

### 101. Why is the absence of a customer ID a limitation?

**Short viva answer**

Without a customer ID, I cannot prove that related records from the same customer are separated across partitions.

**If lecturer asks deeper**

The current grouping protects identical predictor profiles, but it is not a customer-level independence guarantee.

### 102. What is the retrospective snapshot limitation?

**Short viva answer**

Some recorded booking fields may have been updated after the original reservation was created.

**If lecturer asks deeper**

Therefore, the project removes clear outcome leakage but cannot guarantee exact creation-time availability for every retained field.

### 103. What availability limitations remain?

**Short viva answer**

`deposit_type` and `days_in_waiting_list` depend on when the risk assessment is made, and ADR has an unresolved source and timing issue.

**If lecturer asks deeper**

These are timing or source limitations, not all direct leakage. The primary policy retains deposit type and waiting duration but excludes ADR.

### 104. Why is ADR excluded?

**Short viva answer**

ADR is excluded because its source and availability at the intended assessment point are unresolved.

**If lecturer asks deeper**

It is not treated as direct target leakage and may be revisited in a later sensitivity experiment.

### 105. Is the test set a completely untouched external evaluation?

**Short viva answer**

No. It is a holdout partition created from the available dataset, not a prospectively collected external test set.

**If lecturer asks deeper**

Raw EDA happened before the holdout was prepared, so the test set should not be described as an external or prospective evaluation.

### 106. Do you have model performance results?

**Short viva answer**

No. No classifier has been trained and no accuracy, precision, recall, F1-score, or ROC-AUC has been calculated.

**If lecturer asks deeper**

The current results are data understanding, EDA, leakage decisions, preprocessing validation, and partition preparation only.

## L. What Comes Next

### 107. What work is complete?

**Short viva answer**

Data understanding, data-quality investigation, EDA, leakage auditing, preprocessing, feature engineering, and train/test preparation are complete.

**If lecturer asks deeper**

The project has a reproducible primary preparation and a fixed group-aware holdout, but not a trained classifier.

### 108. What comes next?

**Short viva answer**

Next comes model development, model comparison, tuning, and later construction of the final prediction system.

**If lecturer asks deeper**

The general, City-specific, and Resort-specific approaches will be evaluated using the shared holdout design.

### 109. How many algorithms will be evaluated later?

**Short viva answer**

The future plan is to evaluate at least four algorithms.

**If lecturer asks deeper**

The current repository does not contain classifier results, so the exact final ranking of algorithms is not known.

### 110. Which metrics are planned?

**Short viva answer**

The planned metrics are Accuracy, Confusion Matrix, Precision, Recall, F1-score, and ROC-AUC.

**If lecturer asks deeper**

These are future evaluation metrics only. No metrics have been calculated yet.

**Common mistake to avoid**

Do not report future metrics as current results.

### 111. How will tuning be handled?

**Short viva answer**

Tuning and optimization will be performed later using the training data and a leakage-controlled validation process.

**If lecturer asks deeper**

Preprocessing should be refitted within each future training fold, and the holdout should remain reserved for final comparison.

### 112. How will the hotel-specific hypothesis be tested?

**Short viva answer**

I will compare the general approach with City-specific and Resort-specific approaches on the same corresponding holdout bookings.

**If lecturer asks deeper**

City has 63,044 training and 16,119 test records. Resort has 32,331 training and 7,716 test records. The comparison will determine whether differences exist; superiority cannot be assumed.

### 113. When will the final prediction system be built?

**Short viva answer**

It will be built after model development, comparison, and tuning are completed.

**If lecturer asks deeper**

The final system should only be described after the selected model has been evaluated and its limitations have been documented.
