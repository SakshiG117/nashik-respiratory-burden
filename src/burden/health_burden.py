"""Transparent health-burden summaries and scenario calculations.

Observed hospital records are not assumed to be pollution-attributable.
Scenario estimates require an externally justified relative risk and
a matching baseline case count.
"""

from typing import Any

import pandas as pd


def summarize_hospital_records(df: pd.DataFrame) -> dict[str, Any]:
    """Summarize reported hospital records without combining unlike periods."""
    required = {
        "hospital",
        "disease",
        "reported_patients",
        "reporting_period",
        "financial_year",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Hospital dataset is missing columns: {sorted(missing)}"
        )

    data = df.copy()
    data["reported_patients"] = pd.to_numeric(
        data["reported_patients"], errors="coerce"
    )
    data = data.dropna(
        subset=["hospital", "disease", "reported_patients",
                "reporting_period", "financial_year"]
    )

    if (data["reported_patients"] < 0).any():
        raise ValueError("Reported patient counts cannot be negative.")

    grouped = (
        data.groupby(
            ["hospital", "financial_year", "reporting_period", "disease"],
            as_index=False,
        )["reported_patients"]
        .sum()
    )

    return {
        "status": "observed_hospital_records_only",
        "record_count": int(len(data)),
        "groups": grouped.to_dict(orient="records"),
        "warning": (
            "These are reported cases, not confirmed pollution-attributable "
            "cases. Hospitals and reporting periods must not be treated as "
            "directly comparable unless their coverage matches."
        ),
    }


def estimate_attributable_scenario(
    baseline_cases: float,
    relative_risk: float,
) -> dict[str, Any]:
    """Calculate an explicitly assumption-based attributable-case scenario.

    relative_risk must describe the same exposure contrast and outcome
    represented by the supplied baseline cases. This function does not
    estimate or validate either input.
    """
    if baseline_cases < 0:
        raise ValueError("baseline_cases must be non-negative.")
    if relative_risk < 1:
        raise ValueError(
            "relative_risk must be >= 1 for this attributable-fraction "
            "scenario. Supply a justified exposure contrast."
        )

    attributable_fraction = (relative_risk - 1) / relative_risk
    scenario_cases = baseline_cases * attributable_fraction

    return {
        "status": "illustrative_scenario_not_a_local_estimate",
        "baseline_cases": baseline_cases,
        "relative_risk_assumption": relative_risk,
        "attributable_fraction": round(attributable_fraction, 6),
        "scenario_attributable_cases": round(scenario_cases, 2),
        "warning": (
            "Use only when the relative risk is supported by a suitable "
            "health-impact study and matches the baseline outcome, population, "
            "period, and exposure contrast. This is not proof of causation "
            "and is not a validated Nashik estimate."
        ),
    }


def calculate_attributable_burden(
    baseline_cases: float,
    relative_risk: float,
    exposure_increment: float,
    reference_exposure: float,
    observed_exposure: float,
) -> dict[str, Any]:
    """Calculate an illustrative burden scenario using a log-linear RR model.

    relative_risk is the risk ratio per exposure_increment increase.
    All exposure values must use the same units.
    Inputs must match the same population, health outcome and period.
    This function does not validate the epidemiological evidence.
    """
    import math

    values = {
        "baseline_cases": baseline_cases,
        "relative_risk": relative_risk,
        "exposure_increment": exposure_increment,
        "reference_exposure": reference_exposure,
        "observed_exposure": observed_exposure,
    }

    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number.")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")

    if baseline_cases < 0:
        raise ValueError("baseline_cases must be non-negative.")
    if relative_risk < 1:
        raise ValueError("relative_risk must be at least 1.")
    if exposure_increment <= 0:
        raise ValueError("exposure_increment must be positive.")
    if reference_exposure < 0 or observed_exposure < 0:
        raise ValueError("Exposure values must be non-negative.")

    exposure_difference = observed_exposure - reference_exposure

    # This model estimates excess burden only when observed exposure
    # exceeds the reference exposure.
    scaled_rr = relative_risk ** (exposure_difference / exposure_increment)
    attributable_fraction = 1 - (1 / scaled_rr)
    scenario_cases = baseline_cases * attributable_fraction

    return {
        "status": "illustrative_scenario_not_a_validated_local_estimate",
        "baseline_cases": baseline_cases,
        "observed_exposure": observed_exposure,
        "reference_exposure": reference_exposure,
        "exposure_difference": round(exposure_difference, 4),
        "relative_risk_per_increment": relative_risk,
        "exposure_increment": exposure_increment,
        "scaled_relative_risk": round(scaled_rr, 6),
        "attributable_fraction": round(attributable_fraction, 6),
        "scenario_attributable_cases": round(max(0, scenario_cases), 2),
        "warning": (
            "Illustrative calculation only. The relative risk must come "
            "from suitable epidemiological evidence and apply to this "
            "exposure increment, outcome, population and period. The "
            "baseline must be appropriate to the reference exposure. "
            "This is not a validated Nashik estimate."
        ),
    }
