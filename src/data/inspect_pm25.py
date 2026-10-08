import pandas as pd


# ============================================================
# 1. LOAD RAW PM2.5 DATA
# ============================================================

input_file = "data/raw/openaq_pm25_daily_2019_2025.csv"

df = pd.read_csv(input_file)

print("=" * 70)
print("PM2.5 DATA INSPECTION")
print("=" * 70)


# ============================================================
# 2. BASIC INFORMATION
# ============================================================

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 3. CONVERT DATE
# ============================================================

df["date_local"] = pd.to_datetime(
    df["date_local"],
    errors="coerce"
)

print("\nDate conversion completed.")


# ============================================================
# 4. OVERALL DATE RANGE
# ============================================================

print("\nOverall date range:")

print("Minimum:", df["date_local"].min())
print("Maximum:", df["date_local"].max())


# ============================================================
# 5. STATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STATION SUMMARY")
print("=" * 70)

station_summary = (
    df.groupby("station_name")
    .agg(
        records=("value", "count"),
        first_date=("date_local", "min"),
        last_date=("date_local", "max"),
        min_pm25=("value", "min"),
        max_pm25=("value", "max"),
        mean_pm25=("value", "mean")
    )
)

print(station_summary.to_string())


# ============================================================
# 6. MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

print(df.isnull().sum())


# ============================================================
# 7. DUPLICATE RECORDS
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATES")
print("=" * 70)

duplicate_rows = df.duplicated().sum()

print("Duplicate rows:", duplicate_rows)

duplicate_measurements = df.duplicated(
    subset=[
        "station_name",
        "sensor_id",
        "date_local"
    ]
).sum()

print(
    "Duplicate station-sensor-date records:",
    duplicate_measurements
)


# ============================================================
# 8. SENSOR SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SENSOR SUMMARY")
print("=" * 70)

sensor_summary = (
    df.groupby(
        [
            "station_name",
            "sensor_id"
        ]
    )
    .agg(
        records=("value", "count"),
        first_date=("date_local", "min"),
        last_date=("date_local", "max"),
        min_pm25=("value", "min"),
        max_pm25=("value", "max"),
        mean_pm25=("value", "mean")
    )
)

print(sensor_summary.to_string())


# ============================================================
# 9. CHECK NEGATIVE VALUES
# ============================================================

print("\n" + "=" * 70)
print("INVALID PM2.5 VALUES")
print("=" * 70)

negative_values = (df["value"] < 0).sum()

print("Negative PM2.5 values:", negative_values)


# ============================================================
# 10. CHECK EXTREME VALUES
# ============================================================

print("\nHighest PM2.5 observations:")

print(
    df[
        [
            "station_name",
            "sensor_id",
            "date_local",
            "value"
        ]
    ]
    .sort_values("value", ascending=False)
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 11. CHECK DATA BY YEAR
# ============================================================

df["year"] = df["date_local"].dt.year

print("\n" + "=" * 70)
print("RECORDS BY YEAR")
print("=" * 70)

year_summary = (
    df.groupby("year")
    .size()
)

print(year_summary.to_string())


# ============================================================
# 12. CHECK RECORDS BY STATION AND YEAR
# ============================================================

print("\n" + "=" * 70)
print("RECORDS BY STATION AND YEAR")
print("=" * 70)

station_year = pd.crosstab(
    df["station_name"],
    df["year"]
)

print(station_year.to_string())


# ============================================================
# 13. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("INSPECTION COMPLETED")
print("=" * 70)