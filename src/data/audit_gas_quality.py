
import pandas as pd

input_path = "data/processed/other_pollutants_daily_2019_2025.csv"
output_path = "data/processed/other_pollutants_quality_audit.csv"

df = pd.read_csv(input_path)

df["date_local"] = pd.to_datetime(df["date_local"], errors="coerce")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# Preserve existing quality flags, if present.
if "quality_flag" not in df.columns:
    df["quality_flag"] = "check_required"

df["audit_flag"] = "review_not_required"

# Missing measurements
df.loc[df["value"].isna(), "audit_flag"] = "missing_value"

# Negative concentrations
negative = df["value"] < 0
df.loc[negative, "audit_flag"] = "negative_value_review"

# Provisional screening thresholds.
# These flag observations for investigation; they do not prove errors.
thresholds = {
    ("co", "µg/m³"): 10000,
    ("no2", "µg/m³"): 500,
    ("so2", "µg/m³"): 200,
    ("so2", "ppb"): 80,
}

for (parameter, unit), threshold in thresholds.items():
    mask = (
        (df["parameter"] == parameter)
        & (df["unit"] == unit)
        & (df["value"] > threshold)
        & (df["audit_flag"] == "review_not_required")
    )
    df.loc[mask, "audit_flag"] = "high_value_review"

# Save a separate audit dataset.
df.to_csv(output_path, index=False)

print("Quality audit completed.")
print("Rows:", len(df))
print("\nAudit flag counts:")
print(df["audit_flag"].value_counts(dropna=False).to_string())
print("\nFlagged observations:")
print(
    df.loc[df["audit_flag"] != "review_not_required",
           ["station_name", "sensor_id", "parameter",
            "unit", "date_local", "value", "audit_flag"]]
      .to_string(index=False)
)
print("\nSaved to:", output_path)