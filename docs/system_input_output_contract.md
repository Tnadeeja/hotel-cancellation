# Backend prediction input/output contract — Stage 9A

## Frozen model context

Final algorithm: **Random Forest**. Final strategy: **General-only**. Target: `is_canceled`. Output classes: **0 = Not Cancelled**, **1 = Cancelled**. City and Resort both route to the General model.

This system is a prediction interface, not a new modelling or tuning stage. Production must reuse the approved preprocessing and frozen model configuration. No excluded/leakage fields may be requested or used. This document defines the planned contract only; no backend, frontend, saved model, training, evaluation, or prediction is created/executed here.

Authoritative sources inspected: [preprocessing.py](../src/preprocessing.py), [modeling.py](../src/modeling.py), [data dictionary](data_dictionary.md), [preprocessing policy](preprocessing_policy.md), [availability audit](feature_availability_audit.md), [notebook 05](../notebooks/05_preprocessing_feature_engineering.ipynb), [frozen selection](../reports/eval2/frozen_final_selection.csv), [outer-test results](../reports/eval2/final_outer_test_results.csv), and `data/raw/hotel_bookings.csv` (schema/category/missingness/date-representation inspection only; no notebook execution).

The frozen General parameters are `bootstrap=true`, `class_weight="balanced"`, `criterion="gini"`, `max_depth=24`, `max_features=0.5`, `min_samples_leaf=1`, `min_samples_split=2`, `n_estimators=200`, `n_jobs=1`, `random_state=42`. Selection has `outer_test_used=False`; the subsequent saved final evaluation contains Overall, City, and Resort results, all using General-only and threshold 0.5. These are read-only evidence, not instructions to refit.

Assessment must occur before outcome is known, with deposit information available at that point and waiting duration known after confirmation. The retrospective training snapshot does not guarantee original booking-creation values. Do not invent unavailable values or use later outcomes to populate a request.

## Three separate schemas

**A — User/API request:** 22 fields below: 20 required non-null fields plus optional nullable `country` and `agent`. Hotel staff supply booking information and one `arrival_date`.

**B — Internal derivations:** four arrival-date components plus five approved engineered predictors. These nine fields are never accepted as user inputs.

**C — Model predictors:** exactly 30 unencoded columns, ordered as `PREDICTOR_FEATURES` (20 numerical then 10 categorical), before the saved pipeline transforms them. The API-only `arrival_date` is absent here.

The proposed 22-field list matches the source: 25 original retained predictors minus four date components plus one date field = 22 API fields; 21 direct predictors plus four date predictors plus five engineered predictors = 30. No correction to the proposed field list is needed. The date week convention needs the explicit mapping below.

## A — User/API field table

Use strict JSON types: integer means a JSON integer, excluding booleans, strings, fractions, nulls, NaN, and infinity. Binary `is_repeated_guest` uses integer 0/1; a frontend yes/no control sends that representation. All counts below are non-negative integers without arbitrary dataset-derived upper limits. Strings must be nonempty and use exact category spelling/case. Optional fields may be omitted or null; empty strings are invalid, not missing-value aliases.

| API field | User-facing label | Type | Required / Optional | Example | Validation rule | Model fields affected | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hotel | Hotel type | string | Required | Resort Hotel | Fixed category below | hotel | General model for either hotel |
| lead_time | Booking lead time | integer | Required | 342 | >= 0 | lead_time | Preserve recorded booking lead time; do not infer it from today's date |
| arrival_date | Arrival date | string date | Required | 2015-07-01 | Exact YYYY-MM-DD, real calendar date | arrival_date_year, arrival_date_month, arrival_date_week_number, arrival_date_day_of_month | No timestamp/timezone; no historical-year rejection limit |
| stays_in_weekend_nights | Weekend nights | integer | Required | 0 | >= 0 | stays_in_weekend_nights, total_stay_nights | Zero allowed |
| stays_in_week_nights | Week nights | integer | Required | 0 | >= 0 | stays_in_week_nights, total_stay_nights | Both stay counts may be zero |
| adults | Adults | integer | Required | 2 | >= 0; total guests > 0 | adults, total_guests | No adults-only minimum |
| children | Children | integer | Required | 0 | >= 0; total guests > 0 | children, total_guests, family_booking | Raw float64 reflects four missing entries, not permission for fractional children |
| babies | Babies | integer | Required | 0 | >= 0; total guests > 0 | babies, total_guests, family_booking | Explicit count |
| meal | Meal plan | string | Required | BB | Fixed category below | meal | Preserve Undefined |
| country | Country code | string or null | Optional | PRT | When present, exact code from observed country vocabulary | country | Unknown country: omit/null, not a made-up code |
| market_segment | Market segment | string | Required | Direct | Fixed category below | market_segment | Preserve Undefined |
| distribution_channel | Distribution channel | string | Required | Direct | Fixed category below | distribution_channel | Preserve Undefined |
| is_repeated_guest | Repeated guest | integer | Required | 0 | Exactly 0 or 1 | is_repeated_guest | Prior history, not current outcome |
| previous_cancellations | Previous cancellations | integer | Required | 0 | >= 0 | previous_cancellations, previous_booking_total, previous_cancellation_rate | Previous bookings only |
| previous_bookings_not_canceled | Previous non-cancelled bookings | integer | Required | 0 | >= 0 | previous_bookings_not_canceled, previous_booking_total, previous_cancellation_rate | Zero means known no such history |
| reserved_room_type | Reserved room type | string | Required | C | Fixed category below | reserved_room_type | Never use ultimately assigned room |
| deposit_type | Deposit type | string | Required | No Deposit | Fixed category below | deposit_type | Use information available at assessment |
| agent | Agent code | string or null | Optional | 240 | Canonical non-negative decimal integer string: 0 or [1-9][0-9]* | agent | Categorical identifier; omit/null when unknown |
| days_in_waiting_list | Days on waiting list | integer | Required | 0 | >= 0 | days_in_waiting_list | Use known confirmation-time duration |
| customer_type | Customer type | string | Required | Transient | Fixed category below | customer_type | Exact punctuation |
| required_car_parking_spaces | Required parking spaces | integer | Required | 0 | >= 0 | required_car_parking_spaces | Explicit count |
| total_of_special_requests | Special request count | integer | Required | 0 | >= 0 | total_of_special_requests | Explicit count |

Reject `adults + children + babies == 0`, including all three counts zero. Do **not** reject two zero stay counts: Evaluation 1 deliberately retained zero-night records. Observed maxima are context, not rejection limits. Do not require a positive previous history for a repeated guest or otherwise introduce unapproved cross-field business assumptions.

## Categories and missing values

The following are actual non-null raw vocabulary values, checked directly in the dataset. They are suitable dropdown choices and planned strict backend allowlists. Raw vocabulary does not prove every value occurred in the fitted model's training partition.

| Field | Observed values |
| --- | --- |
| hotel | City Hotel; Resort Hotel |
| meal | BB; FB; HB; SC; Undefined |
| market_segment | Aviation; Complementary; Corporate; Direct; Groups; Offline TA/TO; Online TA; Undefined |
| distribution_channel | Corporate; Direct; GDS; TA/TO; Undefined |
| reserved_room_type | A; B; C; D; E; F; G; H; L; P |
| deposit_type | No Deposit; Non Refund; Refundable |
| customer_type | Contract; Group; Transient; Transient-Party |

`country` contains 177 observed non-null uppercase three-character codes, for example PRT, GBR, FRA, and DEU. Use the exact raw vocabulary for a searchable selector; do not substitute display names or assume an external country list is identical. Missing/unknown country is explicit null or omission. A future vocabulary update requires an explicit contract decision rather than silently translating codes.

`agent` is raw float64 because of missing values, but every observed non-null code is integral. Approved preprocessing turns integral numeric values such as 240.0 into string `"240"`; the API therefore accepts the canonical string directly. `"240.0"`, `"0240"`, negative codes, numeric JSON values, and arbitrary text are rejected under this planned API policy. This is stricter than the general source helper, which also stringifies other values; it does not change that helper. New well-formed agent codes can be accepted without claiming they were learned. Missing agent must not be assumed to mean No Agent.

Raw missing counts are children: 4, country: 488, agent: 16,340, company: 112,593; other raw fields have no missing entries. For new operational requests, all guest/stay/history/reservation fields in the required table must be explicitly supplied. Do not use imputation to bypass validation. Only country and agent are nullable in this API contract. Convert their omission/null to actual `numpy.nan` in categorical object columns before the saved pipeline; do not send the literal string `"null"` or user-supplied `"Missing"`.

The existing numerical pipeline uses training-fitted median imputation and StandardScaler. The categorical pipeline uses constant `"Missing"` imputation and `OneHotEncoder(handle_unknown="ignore")`, with empty columns preserved. Reuse fitted transformations; never fit them during a request. Unknown encoded categories produce all-zero indicators for that field, not a learned unseen category. The frontend should guide users toward known values, the backend should reject invalid fixed business categories, and the encoder remains technically tolerant of values absent from its fitted vocabulary, including valid raw categories or new valid agent codes.

## Excluded system inputs

| Field | Reason |
| --- | --- |
| is_canceled | Target, not predictor |
| reservation_status | Outcome leakage |
| reservation_status_date | Outcome leakage |
| assigned_room_type | Approved temporal exclusion: ultimate assignment |
| booking_changes | Approved temporal exclusion: amendments accumulated through outcome |
| company | Approved quality exclusion: extreme missingness/identifier sparsity |
| adr | Approved source/timing exclusion |

Do not reintroduce these because they appear in the CSV. Strict request validation also rejects arrival components, engineered predictors, and any other unexpected field. No customer name, email, phone number, passport number, or other personally identifying information is needed.

## B — Internal derivations

Parse `arrival_date` as a calendar date, then derive:

| Model field | Exact representation |
| --- | --- |
| arrival_date_year | Calendar year as integer (not ISO week-year) |
| arrival_date_month | Full English month name: January through December; fixed English mapping independent of locale |
| arrival_date_week_number | Sunday-start calendar week, with January 1 in week 1; formula below |
| arrival_date_day_of_month | Calendar day integer 1–31, validated by the date |

Week formula: `1 + floor((day_of_year - 1 + jan1_sunday_index) / 7)`, where Sunday=0, Monday=1, ..., Saturday=6 for January 1 of the date's calendar year. With Python Monday=0 weekday numbering, `jan1_sunday_index = (jan1.weekday() + 1) % 7`. This mapping matched every raw arrival row on inspection. **Do not use ISO week numbering or plain strftime %U**: ISO disagreed on 64,054 rows, and %U can have week 0 and different year-start semantics. For example, 2015-07-05 is recorded as week 28, while 2015-07-01 is week 27. The source dictionary leaves the convention unverified; this observational mapping supplies the operational definition without changing training fields.

Reuse `engineer_features()` on a copy of the validated component fields for these five features:

| Engineered field | Approved definition |
| --- | --- |
| total_stay_nights | stays_in_weekend_nights + stays_in_week_nights |
| total_guests | adults + children + babies |
| family_booking | 1 when children > 0 OR babies > 0; 0 when both are zero |
| previous_booking_total | previous_cancellations + previous_bookings_not_canceled |
| previous_cancellation_rate | previous_cancellations / previous_booking_total when total > 0; 0.0 when total == 0 |

The source preserves missing components in sums/history rates; family_booking is positive with either positive child/baby count, zero only with two known zeros, otherwise missing. Required non-null API counts avoid these ambiguous cases, without changing source behavior. Keep original components; invent no additional engineered features. `prepare_training_table()` is a training-table utility requiring the full raw schema and target, not an inference request adapter; do not request excluded fields merely to call it.

## C — Exact final model predictor schema

These tables reproduce `PREDICTOR_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES` in authoritative order. Direct = API value; Date = derived from arrival_date; Engineered = internal approved feature.

| Numerical predictor (20) | Origin |
| --- | --- |
| lead_time | Direct |
| arrival_date_year | Date |
| arrival_date_week_number | Date |
| arrival_date_day_of_month | Date |
| stays_in_weekend_nights | Direct |
| stays_in_week_nights | Direct |
| adults | Direct |
| children | Direct |
| babies | Direct |
| is_repeated_guest | Direct |
| previous_cancellations | Direct |
| previous_bookings_not_canceled | Direct |
| days_in_waiting_list | Direct |
| required_car_parking_spaces | Direct |
| total_of_special_requests | Direct |
| total_stay_nights | Engineered |
| total_guests | Engineered |
| family_booking | Engineered |
| previous_booking_total | Engineered |
| previous_cancellation_rate | Engineered |

| Categorical predictor (10) | Origin |
| --- | --- |
| hotel | Direct |
| arrival_date_month | Date |
| meal | Direct |
| country | Direct, nullable |
| market_segment | Direct |
| distribution_channel | Direct |
| reserved_room_type | Direct |
| deposit_type | Direct |
| agent | Direct, nullable string code |
| customer_type | Direct |

Construct one DataFrame row with exactly these 30 unique columns. Numerical columns must have numeric dtypes; categorical columns must contain the specified strings or normalized missing values. No target, excluded column, group identifier, or API-only arrival_date enters the saved preprocessing/model pipeline. Both hotels use the same General pipeline.

## Successful response

| Response field | Type / meaning |
| --- | --- |
| prediction | Integer 0 or 1 returned by pipeline.predict() |
| prediction_label | Exactly Not Cancelled for 0; Cancelled for 1 |
| cancellation_probability | Finite number in [0,1], pipeline.predict_proba() column for class 1, located using classifier classes_ |
| model_name | Random Forest |
| strategy | General-only |

Use the classifier's existing default decision behavior: the saved evaluation records threshold 0.5; introduce no custom threshold or Low/Medium/High risk bands. Use `predict()` for the class, including its native tie behavior, rather than separately rounding probability. Probability is the model estimate, not a guarantee or a newly calibrated score.

Illustrative response shape only — these values are not a prediction for the example request:

```json
{
  "prediction": 1,
  "prediction_label": "Cancelled",
  "cancellation_probability": 0.73,
  "model_name": "Random Forest",
  "strategy": "General-only"
}
```

## Conceptual error contract

Planned strict request validation rejects unknown fields. Validation failures return no prediction, conceptually HTTP 422 with a stable error code and field-specific messages. Framework implementation is deferred. Malformed JSON is conceptually HTTP 400 (`invalid_json`); an unavailable saved pipeline is conceptually HTTP 503 (`model_unavailable`) and must not trigger training or fabricate a prediction.

```json
{
  "error": "validation_error",
  "details": [
    {"field": "arrival_date", "code": "invalid_date", "message": "arrival_date must be a valid calendar date in YYYY-MM-DD format."}
  ]
}
```

| Invalid situation | Field / code | Example message |
| --- | --- | --- |
| Required field missing/null | hotel / required | hotel is required and must not be null. |
| Invalid date, e.g. 2026-02-30 | arrival_date / invalid_date | arrival_date must be a valid calendar date in YYYY-MM-DD format. |
| Invalid fixed category | hotel / invalid_category | hotel must be City Hotel or Resort Hotel. |
| Negative numeric count | children / out_of_range | children must be an integer greater than or equal to 0. |
| Zero total guests | total_guests / zero_guests | adults + children + babies must be greater than 0. |
| Malformed agent, e.g. 240.0 string | agent / invalid_agent_code | agent must be a canonical non-negative integer string or null. |
| Wrong type, e.g. adults string or boolean | adults / invalid_type | adults must be a JSON integer; strings and booleans are not accepted. |
| Unexpected field | adr / unexpected_field | adr is not an accepted prediction input. |
| Invalid country code | country / invalid_category | country must be an approved dataset code or null when unknown. |

`total_guests` in an error identifies a cross-field rule, not an accepted request field. Do not echo full booking payloads or return raw internal exception traces.

## Stage 10 implications and privacy

Use an arrival date picker; dropdowns for fixed categorical fields; a yes/no toggle that sends 0/1 for repeated guest; non-negative integer inputs for counts; a searchable country selector with an Unknown/null option; and an optional agent text/select control. Expose recorded codes without inventing room-code meanings. The frontend must not ask for engineered predictors or separate arrival components, and must not independently recreate preprocessing logic. Backend validation remains authoritative. Collect only the 22 contract fields, without personal identifiers.

## Intended Stage 9 flow

API request → Pydantic/input validation → derive date features → derive five approved engineered features using the shared source definitions → construct exact 30-predictor DataFrame → saved preprocessing + Random Forest pipeline → predict() → predict_proba() → structured response.

Reuse the saved pipeline's fitted imputation, encoding, scaling, and classifier. Model artifact creation/loading and API implementation are later tasks; this contract does not assert an artifact already exists.

## Example request — no prediction executed

The booking values below reproduce retained input values from the first raw row; arrival_date combines its date components. Both optional fields are included explicitly. Zero stay nights are deliberate and valid.

```json
{
  "hotel": "Resort Hotel",
  "lead_time": 342,
  "arrival_date": "2015-07-01",
  "stays_in_weekend_nights": 0,
  "stays_in_week_nights": 0,
  "adults": 2,
  "children": 0,
  "babies": 0,
  "meal": "BB",
  "country": "PRT",
  "market_segment": "Direct",
  "distribution_channel": "Direct",
  "is_repeated_guest": 0,
  "previous_cancellations": 0,
  "previous_bookings_not_canceled": 0,
  "reserved_room_type": "C",
  "deposit_type": "No Deposit",
  "agent": null,
  "days_in_waiting_list": 0,
  "customer_type": "Transient",
  "required_car_parking_spaces": 0,
  "total_of_special_requests": 0
}
```

Conceptually derived fields (not a prediction):

```json
{
  "arrival_date_year": 2015,
  "arrival_date_month": "July",
  "arrival_date_week_number": 27,
  "arrival_date_day_of_month": 1,
  "total_stay_nights": 0,
  "total_guests": 2,
  "family_booking": 0,
  "previous_booking_total": 0,
  "previous_cancellation_rate": 0.0
}
```

Combine these nine derived values with the 21 direct model inputs, normalize nullable categories, remove arrival_date, and select the source predictor order. No cancellation probability or class has been calculated for this request.

## Contract checklist

- [x] Target excluded.
- [x] Leakage fields excluded.
- [x] Approved feature exclusions preserved.
- [x] 30 final predictors represented.
- [x] 20 numerical predictors represented.
- [x] 10 categorical predictors represented.
- [x] Five engineered features derived internally using engineer_features() definitions.
- [x] Arrival-date components derived internally with observed source week representation.
- [x] Zero-guest requests rejected.
- [x] Zero-night requests allowed.
- [x] Agent treated categorically.
- [x] Optional values documented.
- [x] Successful response schema documented.
- [x] Error response behavior documented.
- [x] No model training performed.
