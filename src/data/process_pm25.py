import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

input_file = "data/raw/openaq_pm25_daily_2019_2025.csv"
output_file = "data/processed/pm25_daily_2019_2025.csv"


# ============================================================
# LOAD RAW DATA
# ============================================================

df = pd.read_csv(input_file)

print("=" * 70)
print("PM2.5 PROCESSING")
print("=" * 70)

print("\nRaw records:", len(df))


# ============================================================
# CONVERT DATE
# ============================================================

df["date_local"] = pd.to_datetime(
    df["date_local"],
    errors="coerce"
)


# ============================================================
# FILTER STUDY PERIOD
# ============================================================

start_date = pd.Timestamp("2019-01-01", tz="Asia/Kolkata")
end_date = pd.Timestamp("2025-12-31 23:59:59", tz="Asia/Kolkata")

df = df[
    (df["date_local"] >= start_date) &
    (df["date_local"] <= end_date)
].copy()

print("Records after date filtering:", len(df))


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

before_duplicates = len(df)

df = df.drop_duplicates()

after_duplicates = len(df)

print("Duplicate records removed:", before_duplicates - after_duplicates)


# ============================================================
# SORT DATA
# ============================================================

df = df.sort_values(
    by=["station_name", "date_local"]
).reset_index(drop=True)


# ============================================================
# ADD YEAR AND MONTH
# ============================================================

df["year"] = df["date_local"].dt.year
df["month"] = df["date_local"].dt.month


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\nProcessed records:", len(df))

print("\nDate range:")
print("Minimum:", df["date_local"].min())
print("Maximum:", df["date_local"].max())

print("\nRecords by station:")
print(
    df.groupby("station_name")
    .size()
    .to_string()
)

print("\nRecords by year:")
print(
    df.groupby("year")
    .size()
    .to_string()
)

print("\nSaved to:")
print(output_file)

print("\n" + "=" * 70)
print("PROCESSING COMPLETED")
print("=" * 70)