# Feature Availability and Leakage Audit

## Prediction Point

The system aims to estimate cancellation risk from reservation information before the final reservation outcome is known. Features that directly reveal the final status or clearly summarize events occurring up to cancellation/check-in must be excluded.

The refined investigation is **Hotel-Type-Specific Cancellation Risk Prediction for City Hotel and Resort Hotel**. Booking-time prediction is not the novelty. Later modelling will investigate whether a general model and hotel-specific models behave differently; superiority is not assumed.

## Classification Rules

- **Project role:** Target; Candidate predictor; Context / grouping feature; Identifier-like feature; Outcome-related feature.
- **Leakage risk:** Direct target leakage; Strong temporal leakage risk; Timing / source limitation; No obvious target leakage identified; N/A — target.
- **Proposed modelling status:** Target; Candidate for modelling; Exclude due to direct leakage; Exclude due to strong temporal concern; Review before final preprocessing.

Availability is described relative to a pre-outcome risk assessment, not exact reservation creation. Final outcome information and strong temporal concerns are excluded; timing/source limitations are held for review. Identifier-related quality and feature-selection issues are separate from leakage. Candidate status does not guarantee usefulness or final retention.

## Retrospective Snapshot Limitation

The source dataset is retrospective and some booking attributes may reflect modifications after the original reservation was created. This project prevents clear outcome leakage but cannot guarantee that every candidate predictor represents its exact value at booking creation. This retrospective snapshot limitation must be acknowledged in later reporting; an updated attribute is not automatically leakage.

Source definitions: [Antonio, Almeida & Nunes, Hotel booking demand datasets, Sections 1–2 and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/) ([DOI](https://doi.org/10.1016/j.dib.2018.11.126)), together with the project interpretations and local descriptive evidence. No network access is needed to execute this notebook.

## Complete Feature Audit

All 32 actual columns are represented in source order. Observed dtypes are retained in the notebook and data dictionary.

| Feature | Role | Availability | Leakage Risk | Proposed Modelling Status | Reason |
| --- | --- | --- | --- | --- | --- |
| hotel | Context / grouping feature | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Hotel type supplies context and the City/Resort grouping; it is constant within a hotel-specific subset. |
| is_canceled | Target | N/A — target | N/A — target | Target | Current reservation outcome; never an input predictor. |
| lead_time | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation timing attribute; amendments to arrival plans are a snapshot limitation, not automatic outcome leakage. |
| arrival_date_year | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Arrival-plan year; a potentially updated plan does not directly reveal the target. |
| arrival_date_month | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Arrival-plan month; subject to the documented retrospective snapshot limitation. |
| arrival_date_week_number | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Arrival-plan week; subject to the documented retrospective snapshot limitation. |
| arrival_date_day_of_month | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Arrival-plan day; subject to the documented retrospective snapshot limitation. |
| stays_in_weekend_nights | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation stay-duration attribute; updates alone do not establish target leakage. |
| stays_in_week_nights | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation stay-duration attribute; updates alone do not establish target leakage. |
| adults | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Guest-count attribute; amendments and unusual counts belong to snapshot/quality limitations. |
| children | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Guest-count attribute; missingness and amendments do not by themselves establish leakage. |
| babies | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Guest-count attribute; no obvious target leakage identified under the revised scope. |
| meal | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation meal category; updates alone are not grounds for a leakage exclusion. |
| country | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Customer/reservation information; corrections, missingness, and cardinality need ordinary quality review. |
| market_segment | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation market classification; no direct final-outcome information identified. |
| distribution_channel | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Booking-channel classification; no obvious target leakage identified. |
| is_repeated_guest | Candidate predictor | Prior customer history | No obvious target leakage identified | Candidate for modelling | Definition refers to customer information/history before the current booking, not its future cancellation outcome. Final retention remains a later selection decision. |
| previous_cancellations | Candidate predictor | Prior customer history | No obvious target leakage identified | Candidate for modelling | Definition refers to customer information/history before the current booking, not its future cancellation outcome. Final retention remains a later selection decision. |
| previous_bookings_not_canceled | Candidate predictor | Prior customer history | No obvious target leakage identified | Candidate for modelling | Definition refers to customer information/history before the current booking, not its future cancellation outcome. Final retention remains a later selection decision. |
| reserved_room_type | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reserved room request remains a candidate and is distinct from the ultimate room assignment. |
| assigned_room_type | Candidate predictor | Later operational assignment | Strong temporal leakage risk | Exclude due to strong temporal concern | Ultimately assigned room may reflect later operations/customer changes; 14,917 codes differ from reserved codes. Not equivalent to reserved_room_type. |
| booking_changes | Candidate predictor | Events accumulated through check-in/cancellation | Strong temporal leakage risk | Exclude due to strong temporal concern | Final count accumulates amendments from entry until check-in/cancellation and may summarize future events; 18,076 positive counts. |
| deposit_type | Candidate predictor | Assessment-time availability needs review | Timing / source limitation | Review before final preprocessing | Based on payments identified before arrival/cancellation; may supply useful pre-outcome information. Review payment timing relative to assessment; do not automatically exclude. |
| agent | Identifier-like feature | Reservation-associated identifier | No obvious target leakage identified | Review before final preprocessing | Identifier-like candidate: 333 observed codes; 16,340 missing (13.686%). Review missing/not-applicable meaning, encoding and usefulness or possible exclusion later; this is not a leakage decision. |
| company | Identifier-like feature | Reservation-associated identifier | No obvious target leakage identified | Review before final preprocessing | Identifier-like candidate: 352 observed codes; 112,593 missing (94.307%). Review missing/not-applicable meaning, encoding and usefulness or possible exclusion later; this is not a leakage decision. |
| days_in_waiting_list | Candidate predictor | Assessment-time availability needs review | Timing / source limitation | Review before final preprocessing | Elapsed time between entry and confirmation can be known after confirmation; suitability depends on the operational assessment point. Not direct leakage or an automatic exclusion. |
| customer_type | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Customer/booking category; possible updates are a documented snapshot limitation. |
| adr | Candidate predictor | Assessment-time availability needs review | Timing / source limitation | Review before final preprocessing | Average Daily Rate is derived from lodging transactions. Verify the source and value known at assessment; retrospective uncertainty is not confirmed temporal leakage or automatic exclusion. |
| required_car_parking_spaces | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation request count; updates alone do not prove leakage. |
| total_of_special_requests | Candidate predictor | Reservation information; retrospective snapshot limitation | No obvious target leakage identified | Candidate for modelling | Reservation request count; possible updates are a snapshot limitation, not a proven outcome summary. |
| reservation_status | Outcome-related feature | Final-outcome information | Direct target leakage | Exclude due to direct leakage | Final reservation status describes the outcome. Observed cross-tabulation: Canceled: target 0=0, target 1=43,017; Check-Out: target 0=75,166, target 1=0; No-Show: target 0=0, target 1=1,207. |
| reservation_status_date | Outcome-related feature | Final-outcome information | Direct target leakage | Exclude due to direct leakage | Date associated with final status is outcome-related information; exclusion does not imply the date alone determines the target. |

## Final Direct Leakage Features

`reservation_status`, `reservation_status_date`. Exclude before modelling.

Canceled: target 0=0, target 1=43,017; Check-Out: target 0=75,166, target 1=0; No-Show: target 0=0, target 1=1,207. The final-status date is excluded for its outcome-event meaning, not because each date determines one target class.

## Strong Temporal Exclusions

`booking_changes` accumulates amendments from entry until check-in/cancellation. `assigned_room_type` describes ultimate allocation and may reflect later operational decisions or customer changes. Both are excluded from the main leakage-controlled model; `reserved_room_type` remains a candidate.

## Timing-Sensitive Features Requiring Review

`days_in_waiting_list` can be known once confirmation occurs, so suitability depends on the assessment point. `deposit_type` reflects payments before arrival/cancellation and may be useful pre-outcome information, with timing to review. `adr` is Average Daily Rate calculated from lodging transactions; its source/value at assessment requires review. These are timing/source limitations, not direct leakage or automatic removal decisions.

## Features Requiring Further Preprocessing Review

`agent` and `company` are identifier-like candidate features requiring preprocessing/feature-selection review, not leakage exclusions. Review high cardinality, missing/not-applicable meaning, possible usefulness, careful encoding, or possible exclusion later.

| Feature | Observed dtype | Unique non-null codes | Missing count | Missing percentage |
| --- | --- | --- | --- | --- |
| agent | float64 | 333 | 16340 | 13.686 |
| company | float64 | 352 | 112593 | 94.307 |

## Candidate Predictors

22 candidate predictors: `hotel`, `lead_time`, `arrival_date_year`, `arrival_date_month`, `arrival_date_week_number`, `arrival_date_day_of_month`, `stays_in_weekend_nights`, `stays_in_week_nights`, `adults`, `children`, `babies`, `meal`, `country`, `market_segment`, `distribution_channel`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`, `reserved_room_type`, `customer_type`, `required_car_parking_spaces`, `total_of_special_requests`. Prior-history definitions refer to activity before the current booking. Candidate status does not guarantee final retention.

No preprocessing or modelling has been performed.
