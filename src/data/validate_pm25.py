import pandas as pd


# ============================================================
# FILE
# ============================================================

input_file = "data/processed/pm25_daily_2019_2025.csv"

df = pd.read_csv(input_file)

df["date_local"] = pd.to_datetime(df["date_local"])


print("=" * 70)
print("PM2.5 VALIDATION")
print("=" * 70)


# ============================================================
# 1. BASIC INFORMATION
# ============================================================

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 2. DATE RANGE
# ============================================================

print("\nDate range:")
print("Minimum:", df["date_local"].min())
print("Maximum:", df["date_local"].max())


# ============================================================
# 3. CHECK STUDY PERIOD
# ============================================================

outside_period = df[
    (df["date_local"] < "2019-01-01") |
    (df["date_local"] > "2025-12-31 23:59:59")
]

print("\nRecords outside 2019–2025:", len(outside_period))


# ============================================================
# 4. DUPLICATE CHECK
# ============================================================

print("\nDuplicate complete rows:", df.duplicated().sum())

duplicate_station_dates = df.duplicated(
    subset=["station_name", "sensor_id", "date_local"]
).sum()

print(
    "Duplicate station-sensor-date records:",
    duplicate_station_dates
)


# ============================================================
# 5. MISSING VALUES
# ============================================================

print("\nMissing values:")
print(df.isnull().sum().to_string())


# ============================================================
# 6. PM2.5 VALUE CHECK
# ============================================================

print("\nPM2.5 statistics:")

print(
    df["value"].describe().to_string()
)

print("\nNegative PM2.5 values:")
print((df["value"] < 0).sum())


# ============================================================
# 7. UNIT CHECK
# ============================================================

print("\nUnits present:")
print(df["unit"].value_counts().to_string())


# ============================================================
# 8. PARAMETER CHECK
# ============================================================

print("\nParameters present:")
print(df["parameter"].value_counts().to_string())


# ============================================================
# 9. STATION COORDINATES
# ============================================================

print("\nStation coordinates:")

coordinates = (
    df.groupby("station_name")
    .agg(
        latitude=("latitude", "nunique"),
        longitude=("longitude", "nunique")
    )
)

print(coordinates.to_string())


# ============================================================
# 10. RECORDS BY STATION
# ============================================================

print("\nRecords by station:")

print(
    df.groupby("station_name")
    .size()
    .to_string()
)


# ============================================================
# 11. RECORDS BY YEAR
# ============================================================

print("\nRecords by year:")

print(
    df.groupby("year")
    .size()
    .to_string()
)


# ============================================================
# 12. CHECK SORTING
# ============================================================

sorted_check = (
    df.sort_values(["station_name", "date_local"])
    .reset_index(drop=True)
)

is_sorted = df.reset_index(drop=True).equals(sorted_check)

print("\nData correctly sorted by station and date:", is_sorted)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)