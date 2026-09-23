# Data Leakage and Feature Availability Findings

## Prediction Point

The system aims to estimate cancellation risk from reservation information before the final reservation outcome is known. Features that directly reveal the final status or clearly summarize events occurring up to cancellation/check-in must be excluded.

The refined investigation is **Hotel-Type-Specific Cancellation Risk Prediction for City Hotel and Resort Hotel**. Booking-time prediction is not the novelty. Later modelling will investigate whether a general model and hotel-specific models behave differently; superiority is not assumed.

## Direct Target Leakage

`reservation_status`, `reservation_status_date` remain direct/outcome leakage exclusions.

Canceled: target 0=0, target 1=43,017; Check-Out: target 0=75,166, target 1=0; No-Show: target 0=0, target 1=1,207. The final-status date is excluded for its outcome-event meaning, not because each date determines one target class.

## Strong Temporal Exclusions

`booking_changes` accumulates amendments from entry until check-in/cancellation. `assigned_room_type` describes ultimate allocation and may reflect later operational decisions or customer changes. Both are excluded from the main leakage-controlled model; `reserved_room_type` remains a candidate.

## Timing / Source Limitations

`days_in_waiting_list` can be known once confirmation occurs, so suitability depends on the assessment point. `deposit_type` reflects payments before arrival/cancellation and may be useful pre-outcome information, with timing to review. `adr` is Average Daily Rate calculated from lodging transactions; its source/value at assessment requires review. These are timing/source limitations, not direct leakage or automatic removal decisions.

## Candidate Predictors

22 normal reservation and prior-history fields remain candidates, including reserved room type, arrival/stay details, guest counts, market/channel information, requests, and hotel type. Possible amendment alone is not leakage. Final retention remains a later selection decision.

## Features Requiring Further Review

Review set: `deposit_type`, `agent`, `company`, `days_in_waiting_list`, `adr`.

`agent` and `company` are identifier-like candidate features requiring preprocessing/feature-selection review, not leakage exclusions. Review high cardinality, missing/not-applicable meaning, possible usefulness, careful encoding, or possible exclusion later.

## Dataset Limitation

The source dataset is retrospective and some booking attributes may reflect modifications after the original reservation was created. This project prevents clear outcome leakage but cannot guarantee that every candidate predictor represents its exact value at booking creation. This retrospective snapshot limitation must be acknowledged in later reporting; an updated attribute is not automatically leakage.

Source definitions: [Antonio, Almeida & Nunes, Hotel booking demand datasets, Sections 1–2 and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/) ([DOI](https://doi.org/10.1016/j.dib.2018.11.126)), together with the project interpretations and local descriptive evidence. No network access is needed to execute this notebook.

## Leakage Prevention Plan

1. Separate the target from predictors.
2. Exclude both direct/outcome fields.
3. Exclude assigned room type and booking changes for strong temporal concerns.
4. Resolve the three timing/source questions and two identifier-treatment questions before final preprocessing; do not automatically remove these fields.
5. Fit learned transformations using training data only, including within validation folds; do not use test-set information.
6. Apply the same approved feature policy to the general, City Hotel, and Resort Hotel models.

The [complete audit](../../docs/feature_availability_audit.md) records every classification. The strict creation-time-only assumption has been removed. No data was transformed, split, or used to train models.
