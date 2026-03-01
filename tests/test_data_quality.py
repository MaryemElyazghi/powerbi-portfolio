"""
Data Quality Test Suite
Run: pytest tests/ -v
"""

import pandas as pd
import numpy as np
import pytest
import os


@pytest.fixture(scope="module")
def df():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "incidents_qualite.csv")
    df = pd.read_csv(path, encoding="utf-8-sig", decimal=",")

    # Force numeric types (handles comma decimal separator)
    df["Cout_Incident"] = pd.to_numeric(df["Cout_Incident"], errors="coerce")
    df["Satisfaction_Score"] = pd.to_numeric(df["Satisfaction_Score"], errors="coerce")
    df["Delai_Resolution_Jours"] = pd.to_numeric(df["Delai_Resolution_Jours"], errors="coerce")
    return df


# ── Schema ────────────────────────────────────────────────────────────────────
def test_required_columns_present(df):
    """All required columns must exist."""
    required = [
        "ID_Incident", "Date_Incident", "Categorie", "Produit",
        "Region", "Statut", "Severite",
        "Delai_Resolution_Jours", "Satisfaction_Score",
        "Cout_Incident", "Technicien", "Resolu"
    ]
    missing = [col for col in required if col not in df.columns]
    assert len(missing) == 0, f"Missing columns: {missing}"


# ── Integrity ─────────────────────────────────────────────────────────────────
def test_no_duplicate_incident_ids(df):
    duplicates = df["ID_Incident"].duplicated().sum()
    assert duplicates == 0, f"{duplicates} duplicate IDs found"


def test_incident_id_format(df):
    pattern = df["ID_Incident"].str.match(r"^INC-\d{5}$")
    invalid = (~pattern).sum()
    assert invalid == 0, f"{invalid} IDs don't match INC-XXXXX format"


# ── Domain Values ─────────────────────────────────────────────────────────────
def test_valid_statut_values(df):
    valid = {"Résolu", "En cours", "Escaladé", "Fermé"}
    invalid = set(df["Statut"].unique()) - valid
    assert len(invalid) == 0, f"Invalid status values: {invalid}"


def test_valid_severite_values(df):
    valid = {"Faible", "Moyen", "Élevé", "Critique"}
    invalid = set(df["Severite"].unique()) - valid
    assert len(invalid) == 0, f"Invalid severity values: {invalid}"


def test_valid_region_values(df):
    valid = {"Casablanca", "Rabat", "Tanger", "Marrakech", "Agadir"}
    invalid = set(df["Region"].unique()) - valid
    assert len(invalid) == 0, f"Invalid region values: {invalid}"


# ── Numeric Ranges ────────────────────────────────────────────────────────────
def test_cout_incident_positive(df):
    """Cost must be numeric and positive."""
    assert df["Cout_Incident"].dtype in [float, "float64"], \
        f"Cout_Incident is not numeric — type: {df['Cout_Incident'].dtype}"
    negative = (df["Cout_Incident"] < 0).sum()
    assert negative == 0, f"{negative} negative costs found"


def test_satisfaction_score_range(df):
    """Satisfaction score must be between 1 and 5."""
    scores = df["Satisfaction_Score"].dropna()
    assert scores.dtype in [float, "float64"], \
        f"Satisfaction_Score is not numeric — type: {scores.dtype}"
    out_of_range = ((scores < 1) | (scores > 5)).sum()
    assert out_of_range == 0, f"{out_of_range} scores outside 1-5 range"


def test_resolu_binary_values(df):
    invalid = (~df["Resolu"].isin([0, 1])).sum()
    assert invalid == 0, f"{invalid} non-binary values in Resolu"


# ── Volume & Dates ────────────────────────────────────────────────────────────
def test_minimum_record_count(df):
    assert len(df) >= 1000, f"Dataset too small: {len(df)} records"


def test_date_range_valid(df):
    dates = pd.to_datetime(df["Date_Incident"])
    assert dates.min().year >= 2023, f"Date too early: {dates.min()}"
    assert dates.max().year <= 2025, f"Date too late: {dates.max()}"


# ── Consistency ───────────────────────────────────────────────────────────────
def test_resolved_incidents_have_delay(df):
    """Resolved incidents should mostly have a delay value."""
    resolved = df[df["Resolu"] == 1]
    missing = resolved["Delai_Resolution_Jours"].isna().sum()
    tolerance = len(resolved) * 0.05  # allow 5% missing
    assert missing <= tolerance, f"Too many missing delays: {missing}"