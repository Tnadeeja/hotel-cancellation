"""Deterministic preparation and train-fitted preprocessing for Evaluation 1.

No function writes datasets or fits a prediction model. Fit the transformer only
after splitting, on training predictors, and reuse it to transform the holdout.
"""

from numbers import Real

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "is_canceled"
DIRECT_LEAKAGE_FEATURES = ("reservation_status", "reservation_status_date")
TEMPORAL_EXCLUSIONS = ("assigned_room_type", "booking_changes")
QUALITY_EXCLUSIONS = ("company",)
PRIMARY_SOURCE_EXCLUSIONS = ("adr",)
EXCLUDED_FEATURES = (
    DIRECT_LEAKAGE_FEATURES + TEMPORAL_EXCLUSIONS
    + QUALITY_EXCLUSIONS + PRIMARY_SOURCE_EXCLUSIONS
)
ENGINEERED_FEATURES = (
    "total_stay_nights", "total_guests", "family_booking",
    "previous_booking_total", "previous_cancellation_rate",
)
CATEGORICAL_FEATURES = (
    "hotel", "arrival_date_month", "meal", "country", "market_segment",
    "distribution_channel", "reserved_room_type", "deposit_type", "agent",
    "customer_type",
)
NUMERICAL_FEATURES = (
    "lead_time", "arrival_date_year", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights", "stays_in_week_nights",
    "adults", "children", "babies", "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "days_in_waiting_list",
    "required_car_parking_spaces", "total_of_special_requests",
) + ENGINEERED_FEATURES
PREDICTOR_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
RAW_FEATURES = (
    tuple(f for f in PREDICTOR_FEATURES if f not in ENGINEERED_FEATURES)
    + EXCLUDED_FEATURES + (TARGET,)
)


def _require_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> None:
    if not df.columns.is_unique:
        raise ValueError("Column names must be unique.")
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"Required columns are missing: {missing}")


def _validate_predictors(X: pd.DataFrame) -> None:
    """Reject target/excluded/unreviewed columns instead of silently passing them."""
    _require_columns(X, PREDICTOR_FEATURES)
    unexpected = sorted(set(X.columns) - set(PREDICTOR_FEATURES))
    if unexpected:
        raise ValueError(f"Unexpected predictor columns: {unexpected}")
    non_numeric = [f for f in NUMERICAL_FEATURES if not pd.api.types.is_numeric_dtype(X[f])]
    if non_numeric:
        raise TypeError(f"Numerical features have non-numeric dtypes: {non_numeric}")
    if X["agent"].notna().any() and not X.loc[X["agent"].notna(), "agent"].map(lambda v: isinstance(v, str)).all():
        raise TypeError("agent must contain string codes or missing values; use prepare_training_table first.")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create five deterministic features on a copy, with no learned statistics.

    Direct addition preserves unknown components. Family status is positive when
    either child/baby count is positive, zero only when both are known zeros,
    and otherwise missing. A zero prior-booking total gives rate 0.0; missing
    history remains missing. Original components are retained.
    """
    required = (
        "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children",
        "babies", "previous_cancellations", "previous_bookings_not_canceled",
    )
    _require_columns(df, required)
    result = df.copy(deep=True)
    result["total_stay_nights"] = result["stays_in_weekend_nights"] + result["stays_in_week_nights"]
    result["total_guests"] = result["adults"] + result["children"] + result["babies"]
    family = pd.Series(np.nan, index=result.index, dtype=float)
    both_zero = result["children"].eq(0) & result["babies"].eq(0)
    any_positive = result["children"].gt(0) | result["babies"].gt(0)
    family.loc[both_zero] = 0.0
    family.loc[any_positive] = 1.0
    result["family_booking"] = family
    total = result["previous_cancellations"] + result["previous_bookings_not_canceled"]
    result["previous_booking_total"] = total
    rate = pd.Series(np.nan, index=result.index, dtype=float)
    rate.loc[total.eq(0)] = 0.0
    positive = total.gt(0)
    rate.loc[positive] = result.loc[positive, "previous_cancellations"] / total.loc[positive]
    result["previous_cancellation_rate"] = rate
    return result


def clean_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Remove only definitively zero-guest rows; retain ambiguous repeated rows.

    Call with the full raw schema, before exclusions or feature engineering.
    Without a booking ID, identical rows cannot be identified as either
    accidental copies or distinct reservations. Preserve their frequency and
    source indices; separate predictor profiles at the later holdout split.
    Unknown guest totals, zero-night stays, and IQR extremes are not filtered.
    """
    _require_columns(df, RAW_FEATURES)
    if set(df.columns) != set(RAW_FEATURES):
        raise ValueError("clean_rows requires exactly the raw schema, before engineering/exclusions.")
    if not df.index.is_unique:
        raise ValueError("Raw row indices must be unique to track partition membership.")
    working = df.copy(deep=True)
    total_guests = working["adults"] + working["children"] + working["babies"]
    # notna makes the rule explicit; unknown components never mean zero guests.
    zero_guests = total_guests.notna() & total_guests.eq(0)
    cleaned = working.loc[~zero_guests].copy()
    counts = {
        "raw_rows": len(df),
        "duplicate_copies_detected": int(df.duplicated(keep="first").sum()),
        "duplicates_removed": 0,
        "zero_guest_rows_removed": int(zero_guests.sum()),
        "final_rows": len(cleaned),
    }
    return cleaned, counts


def _agent_category(value: object) -> object:
    """Keep missingness neutral; remove .0 only from integral numeric codes."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, Real):
        if not np.isfinite(value):
            raise ValueError("Non-finite agent codes require source-data review.")
        return str(int(value)) if float(value).is_integer() else str(value)
    return str(value)


def prepare_training_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return cleaned/engineered primary-model data, retaining the target.

    Retain duplicate-looking rows and remove only definitive zero-guest rows.
    Apply the six approved feature exclusions. Agent is categorical. Represent categorical
    nulls as np.nan for sklearn compatibility without imputing them. All learned
    imputation/encoding/scaling is deferred to the training-only transformer.
    """
    if TARGET not in df or not df[TARGET].isin([0, 1]).all():
        raise ValueError("The target must contain only 0 and 1, without missing values.")
    cleaned, _ = clean_rows(df)
    result = engineer_features(cleaned).drop(columns=list(EXCLUDED_FEATURES))
    result["agent"] = result["agent"].map(_agent_category).astype(object)
    for feature in CATEGORICAL_FEATURES:
        values = result[feature].astype(object)
        result[feature] = values.where(values.notna(), np.nan)
    return result


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate the label on copies; does not partition or fit anything."""
    _require_columns(df, (TARGET,) + PREDICTOR_FEATURES)
    if not df[TARGET].isin([0, 1]).all():
        raise ValueError("The target must contain only 0 and 1, without missing values.")
    X = df.drop(columns=[TARGET]).copy()
    _validate_predictors(X)
    return X, df[TARGET].copy()


def create_predictor_groups(X: pd.DataFrame) -> pd.Series:
    """Return deterministic predictor-only row hashes for holdout grouping.

    Use the final unencoded predictors, before learned imputation/encoding or
    scaling. Validate the schema so target and excluded fields cannot enter.
    Fix column order and exclude the source index from hashing. Missing values
    remain as prepared by prepare_training_table. The signature is a grouping
    identifier, NEVER a model feature or a claim about real booking identity.
    A rare hash collision only co-groups distinct profiles; the notebook also
    checks actual row equality across the resulting partition boundary.
    """
    _validate_predictors(X)
    return pd.util.hash_pandas_object(
        X.loc[:, list(PREDICTOR_FEATURES)], index=False
    ).rename("predictor_group")


def build_preprocessor(X_train: pd.DataFrame) -> ColumnTransformer:
    """Return an UNFITTED transformer with explicit semantic feature groups.

    Fit only with X_train, never X_test or the full table. Agent and hotel are
    categorical regardless of their inferred dtype. Numerical medians, scaling
    statistics, and one-hot vocabularies are learned during the caller's fit.
    keep_empty_features preserves the schema if a training field is all missing
    (sklearn uses 0 for an empty numerical feature); inspect/report such fields.
    """
    _validate_predictors(X_train)
    numerical = Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing", keep_empty_features=True)),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numerical", numerical, list(NUMERICAL_FEATURES)),
        ("categorical", categorical, list(CATEGORICAL_FEATURES)),
    ], remainder="drop", verbose_feature_names_out=True)
