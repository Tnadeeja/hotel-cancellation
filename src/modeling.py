"""Shared, algorithm-independent infrastructure for Evaluation 2.

This module provides training-scope preparation, inner group-aware CV creation,
common scoring definitions, preprocessing-plus-classifier pipeline construction,
and common experiment-result schemas. It does not select or train an algorithm.
The fixed outer holdout remains defined by the approved Evaluation 1 logic and
foundation notebook; this module never creates another outer split. Predictor
groups are partition helpers only, and outer-test data must not be used during
model development or tuning.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from src.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    PREDICTOR_FEATURES,
    build_preprocessor,
)

RANDOM_STATE = 42
INNER_CV_SPLITS = 5
PRIMARY_SCORING = "f1"
POSITIVE_CLASS = 1

GENERAL_SCOPE = "General"
CITY_SCOPE = "City"
RESORT_SCOPE = "Resort"
# MODEL_SCOPES identify where a model is trained and which strategy it represents.
MODEL_SCOPES = (GENERAL_SCOPE, CITY_SCOPE, RESORT_SCOPE)

OVERALL_EVALUATION = "Overall"
CITY_EVALUATION = "City"
RESORT_EVALUATION = "Resort"
# EVALUATION_POPULATIONS identify where later metrics are calculated.
EVALUATION_POPULATIONS = (
    OVERALL_EVALUATION,
    CITY_EVALUATION,
    RESORT_EVALUATION,
)

# Class 1 (Cancelled) is positive; F1 is primary and ROC-AUC uses continuous
# estimator scores when the later estimator supports them.
COMMON_SCORING = {
    "accuracy": "accuracy",
    "precision": make_scorer(
        precision_score,
        pos_label=POSITIVE_CLASS,
        zero_division=0,
    ),
    "recall": make_scorer(
        recall_score,
        pos_label=POSITIVE_CLASS,
        zero_division=0,
    ),
    "f1": make_scorer(
        f1_score,
        pos_label=POSITIVE_CLASS,
        zero_division=0,
    ),
    "roc_auc": "roc_auc",
}

CV_RESULT_COLUMNS = (
    "algorithm",
    "scope",
    "stage",
    "cv_strategy",
    "random_state",
    "parameters",
    "training_rows",
    "predictor_groups",
    "mean_cv_accuracy",
    "std_cv_accuracy",
    "mean_cv_precision",
    "std_cv_precision",
    "mean_cv_recall",
    "std_cv_recall",
    "mean_cv_f1",
    "std_cv_f1",
    "mean_cv_roc_auc",
    "std_cv_roc_auc",
    "tuning_method",
    "best_parameters",
    "observation",
)

OUTER_TEST_RESULT_COLUMNS = (
    "algorithm",
    "scope",
    "evaluation_population",
    "stage",
    "test_rows",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
    "true_negative",
    "false_positive",
    "false_negative",
    "true_positive",
    "observation",
)


def make_inner_cv() -> StratifiedGroupKFold:
    """Return a fresh inner grouped-CV splitter for model development.

    The splitter is used only on an already-defined outer-training population,
    not to create the outer holdout. Callers must supply predictor groups when
    they execute ``split`` or a later CV/search operation.
    """
    return StratifiedGroupKFold(
        n_splits=INNER_CV_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )


def _validate_scope_inputs(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
) -> None:
    """Validate one aligned outer-training scope without mutating inputs."""
    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a pandas DataFrame.")
    if not isinstance(y, pd.Series):
        raise ValueError("y must be a pandas Series.")
    if not isinstance(groups, pd.Series):
        raise ValueError("groups must be a pandas Series.")
    if not X.columns.is_unique:
        raise ValueError("X must have unique predictor column names.")
    if not (len(X) == len(y) == len(groups)):
        raise ValueError("X, y, and groups must have equal lengths.")
    if not X.index.equals(y.index) or not X.index.equals(groups.index):
        raise ValueError("X, y, and groups must have identical indexes.")
    if len(X.columns) != len(PREDICTOR_FEATURES):
        raise ValueError("X must contain exactly 30 predictor columns.")
    if set(X.columns) != set(PREDICTOR_FEATURES):
        raise ValueError("X columns must exactly match the approved predictors.")
    if len(NUMERICAL_FEATURES) != 20 or len(CATEGORICAL_FEATURES) != 10:
        raise ValueError("The numerical/categorical feature counts are not approved.")
    numerical_features = set(NUMERICAL_FEATURES)
    categorical_features = set(CATEGORICAL_FEATURES)
    if numerical_features.intersection(categorical_features):
        raise ValueError("Numerical and categorical predictors must be disjoint.")
    if numerical_features.union(categorical_features) != set(PREDICTOR_FEATURES):
        raise ValueError("Numerical and categorical predictors must cover all predictors.")
    if y.isna().any() or not set(y.unique()).issubset({0, 1}):
        raise ValueError("y must contain only non-missing binary values 0 and 1.")
    if groups.isna().any():
        raise ValueError("groups must not contain missing group IDs.")
    if "predictor_group" in X.columns:
        raise ValueError("groups must remain separate from the X feature matrix.")


def create_training_scopes(
    X_train_outer: pd.DataFrame,
    y_train_outer: pd.Series,
    groups_train_outer: pd.Series,
) -> dict[str, dict[str, pd.Series | pd.DataFrame]]:
    """Create aligned General, City, and Resort scopes from outer training data.

    No split is created, indexes are preserved, and the ``hotel`` predictor is
    retained in every returned scope. The supplied data must already be the
    approved outer-training population.
    """
    _validate_scope_inputs(X_train_outer, y_train_outer, groups_train_outer)

    hotel_values = set(X_train_outer["hotel"].dropna().unique())
    if X_train_outer["hotel"].isna().any():
        raise ValueError("The approved outer-training population must not have missing hotel values.")
    if hotel_values != {"City Hotel", "Resort Hotel"}:
        raise ValueError(
            "The approved outer-training population must contain exactly "
            "'City Hotel' and 'Resort Hotel' hotel labels."
        )

    scope_masks = {
        GENERAL_SCOPE: pd.Series(True, index=X_train_outer.index),
        CITY_SCOPE: X_train_outer["hotel"].eq("City Hotel"),
        RESORT_SCOPE: X_train_outer["hotel"].eq("Resort Hotel"),
    }
    scopes: dict[str, dict[str, pd.Series | pd.DataFrame]] = {}
    for scope_name, mask in scope_masks.items():
        scope = {
            "X": X_train_outer.loc[mask].copy(),
            "y": y_train_outer.loc[mask].copy(),
            "groups": groups_train_outer.loc[mask].copy(),
        }
        _validate_scope_inputs(scope["X"], scope["y"], scope["groups"])
        scopes[scope_name] = scope

    for scope_name, expected_hotel in (
        (CITY_SCOPE, "City Hotel"),
        (RESORT_SCOPE, "Resort Hotel"),
    ):
        hotel_values = scopes[scope_name]["X"]["hotel"].dropna().unique()
        if len(hotel_values) != 1 or hotel_values[0] != expected_hotel:
            raise ValueError(f"{scope_name} scope must contain only {expected_hotel!r}.")

    if len(scopes[CITY_SCOPE]["X"]) + len(scopes[RESORT_SCOPE]["X"]) != len(scopes[GENERAL_SCOPE]["X"]):
        raise ValueError("City and Resort scopes must partition the General scope completely.")
    if len(scopes[CITY_SCOPE]["X"].index.intersection(scopes[RESORT_SCOPE]["X"].index)) != 0:
        raise ValueError("City and Resort scope indexes must be disjoint.")

    return scopes


def summarize_training_scopes(
    scopes: dict[str, dict[str, pd.Series | pd.DataFrame]],
) -> pd.DataFrame:
    """Return descriptive row, cancellation-rate, and group counts per scope."""
    for scope_name in MODEL_SCOPES:
        if scope_name not in scopes:
            raise ValueError(f"Missing required scope: {scope_name}.")
        scope = scopes[scope_name]
        _validate_scope_inputs(scope["X"], scope["y"], scope["groups"])

    return pd.DataFrame(
        [
            {
                "scope": scope_name,
                "rows": len(scopes[scope_name]["X"]),
                "cancellation_rate": scopes[scope_name]["y"].mean(),
                "unique_predictor_groups": scopes[scope_name]["groups"].nunique(),
            }
            for scope_name in MODEL_SCOPES
        ]
    )


def build_model_pipeline(X_reference: pd.DataFrame, estimator: Any) -> Pipeline:
    """Build an unfitted preprocessing-plus-estimator pipeline.

    Future CV/search utilities must clone and fit this complete pipeline within
    each fold. Keeping preprocessing inside the pipeline ensures that median
    imputation, scaling statistics, and one-hot vocabularies are learned only
    from each fold's training rows. This function does not fit or alter the
    supplied estimator.
    """
    if not isinstance(X_reference, pd.DataFrame):
        raise ValueError("X_reference must be a pandas DataFrame.")
    if not X_reference.columns.is_unique:
        raise ValueError("X_reference must have unique predictor column names.")
    if len(X_reference.columns) != len(PREDICTOR_FEATURES):
        raise ValueError("X_reference must contain exactly 30 predictor columns.")
    if set(X_reference.columns) != set(PREDICTOR_FEATURES):
        raise ValueError("X_reference columns must exactly match the approved predictors.")
    return Pipeline(
        [
            ("preprocessor", build_preprocessor(X_reference)),
            ("classifier", estimator),
        ]
    )


def make_empty_cv_result() -> dict[str, Any]:
    """Return an unpopulated record with the shared CV-result schema."""
    return {column: None for column in CV_RESULT_COLUMNS}


def make_empty_outer_test_result() -> dict[str, Any]:
    """Return an unpopulated record with the shared outer-test schema."""
    return {column: None for column in OUTER_TEST_RESULT_COLUMNS}


__all__ = [
    "RANDOM_STATE",
    "INNER_CV_SPLITS",
    "PRIMARY_SCORING",
    "POSITIVE_CLASS",
    "MODEL_SCOPES",
    "EVALUATION_POPULATIONS",
    "COMMON_SCORING",
    "CV_RESULT_COLUMNS",
    "OUTER_TEST_RESULT_COLUMNS",
    "make_inner_cv",
    "create_training_scopes",
    "summarize_training_scopes",
    "build_model_pipeline",
    "make_empty_cv_result",
    "make_empty_outer_test_result",
]
