# Air Quality Data Quality Notes

## CO Sensor Review

* The older Gangapur Road CO sensor (ID 14868) reports values in µg/m³.
* Newer CO sensors report values in ppb.
* The OpenAQ sensor metadata confirms these reported units.
* Daily and original 15-minute records from the newer Gangapur Road sensor contain low values around 0.7 ppb.
* The inspected API records did not report flags, but this does not independently verify sensor calibration or measurement accuracy.

**Decision:** Retain the original measurements, but exclude CO from the initial model until its scale and comparability are verified.

## Other Gas Quality Flags

* Unusually high CO, NO₂, and SO₂ observations are flagged for review.
* Negative SO₂ observations are flagged for review.
* Missing values are retained as missing.
* Flagged observations are not automatically deleted.

## Data Handling Principles

* Preserve raw downloaded data.
* Keep quality flags in processed datasets.
* Do not interpolate large monitoring gaps without a justified method.
* Do not combine measurements reported in different units without a documented conversion.
* Distinguish verified measurements from observations that still require review.
