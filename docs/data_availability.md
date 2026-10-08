# Nashik Data Availability Sheet

This document records the availability, source, frequency, spatial coverage,
and access method of datasets required for the respiratory disease burden
estimation prototype.

| Dataset | Source | Years Available | Frequency | Nashik Coverage | Missing % | Access Method | Status |
|---|---|---|---|---|---|---|---|
| PM2.5 | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| PM10 | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| NO2 | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| SO2 | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| CO | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| O3 | CPCB / OpenAQ | To verify | Hourly/Daily | To verify | To calculate | API/Download | Pending |
| Temperature | ERA5-Land / Weather API | To verify | Hourly/Daily | Nashik | To calculate | API/Download | Pending |
| Relative Humidity | ERA5-Land / Weather API | To verify | Hourly/Daily | Nashik | To calculate | API/Download | Pending |
| Wind Speed | ERA5-Land / Weather API | To verify | Hourly/Daily | Nashik | To calculate | API/Download | Pending |
| Rainfall | ERA5-Land / Weather API | To verify | Daily/Monthly | Nashik | To calculate | API/Download | Pending |
| MODIS AOD | NASA MODIS MAIAC MCD19A2 | To verify | Daily | Nashik | To calculate | Google Earth Engine | Pending |
| Population | Census / WorldPop | To verify | Annual/Available years | Nashik | To calculate | Download/API | Pending |
| Respiratory Health Data | Health Department / Published Data | To verify | Monthly/Annual | Nashik | To calculate | Dataset/Report | Pending |

## Target Study Area

Nashik city, Maharashtra, India.

## Target Historical Period

2019–2025, subject to actual data availability.

## Primary Pollutant

PM2.5.

## Secondary Pollutants

PM10, NO2, SO2, CO and O3, subject to data availability.

## Important Notes

- Do not assume that a dataset is available for all years.
- Verify actual Nashik monitoring-station coverage before using air-quality data.
- Record missing values after obtaining the data.
- Do not fabricate missing health cases, hospital admissions or mortality data.
- If reliable Nashik-specific health data are unavailable, use an epidemiological
  attributable-burden methodology based on published concentration-response
  relationships and clearly label the result as estimated burden.
- Raw data should be preserved in `data/raw/`.
- Cleaned datasets should be stored in `data/processed/`.
- External reference datasets should be stored in `data/external/`.