import pandas as pd


# ============================================================
# LOAD DATA
# ============================================================

input_file = "data/raw/openaq_pm25_daily_2019_2025.csv"

df = pd.read_csv(input_file)

df["date_local"] = pd.to_datetime(df["date_local"])


# ============================================================
# KEEP ONLY OUR INITIAL STUDY PERIOD
# ============================================================

df = df[
    (df["date_local"] >= "2019-01-01") &
    (df["date_local"] <= "2025-12-31")
].copy()


# ============================================================
# CHECK GAPS FOR EACH SENSOR
# ============================================================

print("=" * 70)
print("PM2.5 GAP ANALYSIS — 2019 TO 2025")
print("=" * 70)

for sensor_id, group in df.groupby("sensor_id"):

    group = group.sort_values("date_local")

    dates = group["date_local"].dt.date

    full_range = pd.date_range(
        start=group["date_local"].min(),
        end=group["date_local"].max(),
        freq="D"
    )

    existing_dates = pd.DatetimeIndex(
        group["date_local"].dt.normalize().unique()
    )

    missing_dates = full_range.difference(existing_dates)

    print("\n" + "-" * 70)
    print("Station:", group["station_name"].iloc[0])
    print("Sensor:", sensor_id)
    print("Available records:", len(group))
    print("First date:", group["date_local"].min())
    print("Last date:", group["date_local"].max())
    print("Expected calendar days:", len(full_range))
    print("Missing days:", len(missing_dates))

    if len(missing_dates) > 0:
        print("First 10 missing dates:")
        print(missing_dates[:10].strftime("%Y-%m-%d").tolist())


# ============================================================
# YEARLY COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("YEARLY COVERAGE")
print("=" * 70)

df["year"] = df["date_local"].dt.year

yearly = (
    df.groupby(["station_name", "sensor_id", "year"])
    .size()
    .reset_index(name="records")
)

print(yearly.to_string(index=False))


print("\n" + "=" * 70)
print("GAP ANALYSIS COMPLETED")
print("=" * 70)