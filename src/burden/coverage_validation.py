from __future__ import annotations

import pandas as pd


def validate_seasonal_coverage(
    air_quality: pd.DataFrame,
    start_date: str,
    end_date: str,
    minimum_coverage: float = 0.80,
) -> dict:
    """Check daily PM2.5 coverage for a specified hospital reporting period.

    Coverage is the fraction of calendar days with at least one valid PM2.5
    observation. This is a data-completeness check, not a health-burden estimate.
    """
    required = {"date_local", "pm25_value"}
    missing = required - set(air_quality.columns)
    if missing:
        raise ValueError(f"Air-quality data is missing columns: {sorted(missing)}")

    if not 0 < minimum_coverage <= 1:
        raise ValueError("minimum_coverage must be greater than 0 and at most 1.")

    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()

    if end < start:
        raise ValueError("end_date must be on or after start_date.")

    dates = pd.to_datetime(air_quality["date_local"], errors="coerce").dt.normalize()
    pm25 = pd.to_numeric(air_quality["pm25_value"], errors="coerce")
    valid = pm25.notna() & pm25.ge(0) & dates.notna()

    in_period = valid & dates.ge(start) & dates.le(end)
    observed_days = int(dates[in_period].nunique())
    expected_days = int((end - start).days + 1)
    coverage = observed_days / expected_days

    return {
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "expected_days": expected_days,
        "observed_days": observed_days,
        "missing_days": expected_days - observed_days,
        "coverage_fraction": round(coverage, 4),
        "coverage_percent": round(coverage * 100, 2),
        "minimum_coverage_percent": round(minimum_coverage * 100, 2),
        "sufficient_coverage": coverage >= minimum_coverage,
        "status": (
            "coverage_sufficient_for_review"
            if coverage >= minimum_coverage
            else "insufficient_coverage"
        ),
        "warning": (
            "Coverage measures data completeness only. It does not establish "
            "causation or validate a pollution-attributable health-burden estimate."
        ),
    }
