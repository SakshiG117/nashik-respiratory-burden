
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.burden.coverage_validation import validate_seasonal_coverage
from src.burden.health_burden import summarize_hospital_records

# Project root: the folder containing src/
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

app = FastAPI(
    title="Nashik Respiratory Burden API",
    description=(
        "Prototype API for Nashik air-quality monitoring, "
        "ward demographics, and source-labelled hospital records."
    ),
    version="0.1.0",
)

# Development only. Restrict origins before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def load_csv(relative_path: str) -> pd.DataFrame:
    path = DATA / relative_path
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Required dataset not found: {relative_path}",
        )
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read dataset: {relative_path}",
        ) from exc


@app.get("/")
def home():
    return {
        "project": "Nashik Respiratory Disease Burden Estimation",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/overview")
def overview():
    pm = load_csv("processed/pm25_daily_2019_2025.csv")
    wards = load_csv("raw/nashik_wards_geographic_data.csv")

    pm["date_local"] = pd.to_datetime(pm["date_local"], errors="coerce")
    pm["value"] = pd.to_numeric(pm["value"], errors="coerce")
    valid = pm.dropna(subset=["date_local", "value"])

    latest_date = valid["date_local"].max()
    latest_rows = valid[valid["date_local"] == latest_date]

    return {
        "city": "Nashik",
        "ward_count": int(wards["ward_no"].nunique()),
        "ward_population_total": int(wards["tot_p"].sum()),
        "pm25_record_count": int(len(valid)),
        "station_count": int(valid["station_name"].nunique()),
        "latest_available_date": (
            latest_date.strftime("%Y-%m-%d") if pd.notna(latest_date) else None
        ),
        "latest_pm25_average_ug_m3": (
            round(float(latest_rows["value"].mean()), 2)
            if not latest_rows.empty else None
        ),
        "population_reference": "Ward dataset; reference year to be verified",
        "health_burden_status": (
            "Not inferred from PM2.5 alone; see source-labelled hospital records"
        ),
    }


@app.get("/api/trends")
def trends():
    pm = load_csv("processed/pm25_daily_2019_2025.csv")
    pm["date_local"] = pd.to_datetime(pm["date_local"], errors="coerce")
    pm["value"] = pd.to_numeric(pm["value"], errors="coerce")
    pm = pm.dropna(subset=["date_local", "value"])

    grouped = (
        pm.assign(date=pm["date_local"].dt.strftime("%Y-%m-%d"))
        .groupby("date", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "pm25_ug_m3"})
    )

    return {
        "unit": "µg/m³",
        "aggregation": "Mean of available station records per date",
        "note": "Missing dates indicate unavailable records, not zero pollution.",
        "data": grouped.to_dict(orient="records"),
    }


@app.get("/api/stations")
def stations():
    pm = load_csv("processed/pm25_daily_2019_2025.csv")
    pm["date_local"] = pd.to_datetime(pm["date_local"], errors="coerce")
    pm["value"] = pd.to_numeric(pm["value"], errors="coerce")
    pm = pm.dropna(subset=["date_local", "value"])

    results = []
    for station, group in pm.groupby("station_name"):
        latest_date = group["date_local"].max()
        latest = group[group["date_local"] == latest_date].iloc[-1]

        results.append({
            "station_name": str(station),
            "latitude": float(latest["latitude"]),
            "longitude": float(latest["longitude"]),
            "latest_available_date": latest_date.strftime("%Y-%m-%d"),
            "latest_pm25_ug_m3": round(float(latest["value"]), 2),
            "record_count": int(len(group)),
        })

    return {"unit": "µg/m³", "stations": results}


@app.get("/api/wards")
def wards():
    df = load_csv("raw/nashik_wards_geographic_data.csv")

    result = df[["ward_no", "name", "tot_p", "Pop_Den"]].copy()
    result = result.rename(columns={
        "ward_no": "ward_number",
        "name": "ward_name",
        "tot_p": "population",
        "Pop_Den": "population_density_source_value",
    })
    result = result.sort_values("ward_number")

    return {
        "count": int(len(result)),
        "note": (
            "Census-style ward attributes; density units and reference year "
            "must be verified. These are not ward-level pollution measurements."
        ),
        "wards": result.to_dict(orient="records"),
    }



@app.get("/api/hospital-records")
def hospital_records():
    df = load_csv("raw/combined_hospital_health_records.csv")

    return {
        "record_count": int(len(df)),
        "source_note": (
            "Records from Civil Hospital Nashik, ESIC Hospital, and "
            "Life Care Super Speciality Hospital. Sources and reporting "
            "periods differ; these are not citywide totals or "
            "pollution-attributable cases."
        ),
        "records": df.to_dict(orient="records"),
    }


@app.get("/api/hospital-comparison")
def hospital_comparison():
    df = load_csv("raw/combined_hospital_health_records.csv")

    grouped = (
        df.groupby(
            ["financial_year", "hospital", "disease", "reporting_period"],
            as_index=False,
        )["reported_patients"]
        .sum()
    )

    return {
        "note": (
            "Compare records within matching reporting periods and "
            "geographic coverage. Annual Civil Hospital counts should "
            "not be directly compared with three-month assessment counts."
        ),
        "data": grouped.to_dict(orient="records"),
    }

@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(ROOT / "dashboard" / "index.html")
from src.burden.health_burden import summarize_hospital_records


@app.get("/api/burden-summary")
def burden_summary():
    df = load_csv("raw/combined_hospital_health_records.csv")
    summary = summarize_hospital_records(df)

    air = load_csv("processed/air_quality_weather_daily_2019_2025.csv")

    periods = [
        {
            "label": "December 2023–February 2024",
            "start_date": "2023-12-01",
            "end_date": "2024-02-29",
        },
        {
            "label": "December 2024–February 2025",
            "start_date": "2024-12-01",
            "end_date": "2025-02-28",
        },
    ]

    coverage_results = [
        {
            "label": period["label"],
            **validate_seasonal_coverage(
                air,
                period["start_date"],
                period["end_date"],
            ),
        }
        for period in periods
    ]

    summary["air_quality_coverage"] = coverage_results
    summary["burden_estimate_status"] = (
        "not_estimated_insufficient_exposure_coverage"
    )

    return summary