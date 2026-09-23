# Data Dictionary

Source: `data/raw/hotel_bookings.csv`, inspected in `notebooks/01_data_understanding.ipynb`. The table contains one row per observed column, in source order.

Data types are the observed pandas 3.0.3 CSV-inferred dtypes. Inference may differ across pandas versions; these types do not establish final semantic or modelling roles. Descriptions are conservative interpretations of names and project context, not a verified source codebook. Unconfirmed units, codes, and event definitions require dataset documentation.

Roles, leakage risks, and proposed decisions follow [the revised pre-outcome audit](feature_availability_audit.md). Normal reservation attributes and prior customer history remain candidates. Identifier treatment is a preprocessing/feature-selection issue; timing/source limitations are distinct from confirmed leakage.

The source dataset is retrospective and some booking attributes may reflect modifications after the original reservation was created. This project prevents clear outcome leakage but cannot guarantee that every candidate predictor represents its exact value at booking creation. This retrospective snapshot limitation must be acknowledged in later reporting; an updated attribute is not automatically leakage.

| Feature | Description | Data Type | Role | Leakage Risk | Preprocessing Decision |
|---|---|---|---|---|---|
| hotel | Hotel type recorded for the booking; central to the City Hotel versus Resort Hotel investigation. | str | Context / grouping feature | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| is_canceled | Recorded cancellation outcome: 0 = Not Cancelled; 1 = Cancelled. | int64 | Target | N/A — target | Target — separate from predictors |
| lead_time | Booking lead time; exact interval definition and unit to be verified from dataset documentation. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| arrival_date_year | Year of the recorded arrival date. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| arrival_date_month | Month of the recorded arrival date. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| arrival_date_week_number | Week number of the recorded arrival date; week numbering convention requires verification. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| arrival_date_day_of_month | Day of the month of the recorded arrival date. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| stays_in_weekend_nights | Number of weekend nights recorded for the stay; weekend definition requires verification. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| stays_in_week_nights | Number of weekday nights recorded for the stay; weekday definition requires verification. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| adults | Number of adults recorded for the booking. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| children | Number of children recorded for the booking. | float64 | Candidate predictor | No obvious target leakage identified | Retain; training-fitted median imputation and standardization |
| babies | Number of babies recorded for the booking. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| meal | Meal category recorded for the booking; category codes require verification. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| country | Country code recorded for the booking; exact interpretation and coding standard require verification. | str | Candidate predictor | No obvious target leakage identified | Retain; categorical Missing imputation and training-fitted one-hot encoding |
| market_segment | Market segment recorded for the booking. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| distribution_channel | Distribution channel recorded for the booking. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| is_repeated_guest | Indicator of repeated-guest status; coding requires verification. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| previous_cancellations | Count of previous cancellations recorded for the guest. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| previous_bookings_not_canceled | Count of previous bookings recorded as not cancelled for the guest. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| reserved_room_type | Reserved room-type code; code meanings require verification. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| assigned_room_type | Assigned room-type code; code meanings require verification. | str | Candidate predictor | Strong temporal leakage risk | Exclude before modelling — strong temporal concern |
| booking_changes | Number of booking changes recorded; counting rules require verification. | int64 | Candidate predictor | Strong temporal leakage risk | Exclude before modelling — strong temporal concern |
| deposit_type | Deposit category recorded for the booking. | str | Candidate predictor | Timing / source limitation | Retain as categorical; timing limitation documented; Missing imputation and one-hot encoding |
| agent | Agent-related code; identifier interpretation requires verification. | float64 | Identifier-like feature | No obvious target leakage identified | Retain as categorical identifier; impute Missing category on training pipeline; one-hot encode |
| company | Company-related code; identifier interpretation requires verification. | float64 | Identifier-like feature | No obvious target leakage identified | Exclude from primary model — extreme missingness / identifier-like sparsity |
| days_in_waiting_list | Number of days recorded on a waiting list. | int64 | Candidate predictor | Timing / source limitation | Retain as numerical; timing limitation documented; training-fitted median imputation and standardization |
| customer_type | Customer category recorded for the booking. | str | Candidate predictor | No obvious target leakage identified | Retain as categorical; Missing imputation and training-fitted one-hot encoding |
| adr | Average Daily Rate (ADR); in the source dataset it is calculated from lodging transactions divided by the number of staying nights. | float64 | Candidate predictor | Timing / source limitation | Exclude from primary model — unresolved timing/source limitation; optional sensitivity analysis later |
| required_car_parking_spaces | Number of car parking spaces requested for the booking. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| total_of_special_requests | Number of special requests recorded for the booking. | int64 | Candidate predictor | No obvious target leakage identified | Retain as numerical; training-fitted median imputation and standardization |
| reservation_status | Recorded reservation status; status timing and definitions require verification. | str | Outcome-related feature | Direct target leakage | Exclude before modelling — direct leakage |
| reservation_status_date | Date associated with the recorded reservation status; exact event definition requires verification. | str | Outcome-related feature | Direct target leakage | Exclude before modelling — direct leakage |

## Implemented Preprocessing Decisions

The source-column decisions above reflect [the preprocessing policy](preprocessing_policy.md). Roles and leakage-risk labels from the audit are preserved; quality/source exclusions remain distinct from direct leakage. Raw data is unchanged.

## Engineered Features

These five features are created on the modelling copy only. Each enters the numerical branch with training-fitted median imputation and standardization. No source columns are replaced.

| Feature | Formula / rule | Purpose / missingness |
| --- | --- | --- |
| total_stay_nights | stays_in_weekend_nights + stays_in_week_nights | Planned/recorded total stay; zero is retained |
| total_guests | adults + children + babies | Party size; any missing component leaves the total missing |
| family_booking | 1 if children > 0 or babies > 0; 0 if both are known zeros; otherwise missing | Recorded child/baby presence; not a claim about relationships |
| previous_booking_total | previous_cancellations + previous_bookings_not_canceled | Amount of prior booking history |
| previous_cancellation_rate | previous_cancellations / previous_booking_total when >0; 0.0 when total=0 | Observed prior cancellation share; unknown history stays missing |
