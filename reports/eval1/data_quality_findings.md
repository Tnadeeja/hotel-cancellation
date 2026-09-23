# Data Quality Findings

## Dataset

Source: `data/raw/hotel_bookings.csv`. Shape: **119,390 rows × 32 columns**. Calculated in `notebooks/02_data_quality_audit.ipynb` using pandas 3.0.3. Percentages use all rows unless labelled within-hotel or non-null. Audit only; no cleaning or preprocessing has been applied.

## Missing Values

company: 112,593 (94.307%); agent: 16,340 (13.686%); country: 488 (0.409%); children: 4 (0.003%). Missing does not automatically mean incorrect.

## Duplicate Records

31,994 extra identical copies (26.798% of rows); 40,165 rows belong to repeated groups (33.642%). There are 87,396 distinct full-row patterns, 8,171 repeated groups, and a maximum identical-row frequency of 180. Duplicates have not been removed. Without an obvious unique booking identifier, identical records cannot automatically be treated as accidental duplicates.

## Unusual / Potentially Invalid Values

Zero total guests: 180 (0.151%); zero total stay: 715 (0.599%). Guest totals are unevaluable for 4 records because at least one component is missing. ADR ranges from -6.38 to 5400; 1 negative and 1,959 zero ADR records. The 16 basic validity checks produced 0 flags (counts may overlap). Unexpected hotel-category rows: 0. These checks do not establish that every record is valid; unusual observations need context.

### Categorical consistency

Among 12 text columns, detected 0 empty-string cells, 0 whitespace-only cells, 0 cells with edge whitespace, and 0 case-variant groups. These checks describe parsed values; default CSV parsing may represent empty fields and recognised missing tokens as nulls. Context labels below are not automatically invalid.

| Feature | Observation | Example | Rows |
| --- | --- | --- | --- |
| meal | Context label | 'Undefined' | 1169 |
| market_segment | Context label | 'Undefined' | 2 |
| distribution_channel | Context label | 'Undefined' | 5 |

## Outlier Candidates

The 1.5 × IQR screen flagged 64,004 distinct records (53.609%) in at least one of 13 selected measurements/counts. 8 screened fields have IQR = 0. An IQR flag is not evidence of an invalid record. Feature counts overlap, and percentages in the feature table use non-null counts. No observations were removed or capped; contextual investigation and later EDA are required.

| Feature | IQR | Outside bounds | Percentage of non-null |
| --- | --- | --- | --- |
| lead_time | 142.000 | 3005 | 2.517 |
| adr | 56.710 | 3793 | 3.177 |
| stays_in_weekend_nights | 2.000 | 265 | 0.222 |
| stays_in_week_nights | 2.000 | 3354 | 2.809 |
| adults | 0.000 | 29710 | 24.885 |
| children | 0.000 | 8590 | 7.195 |
| babies | 0.000 | 917 | 0.768 |
| previous_cancellations | 0.000 | 6484 | 5.431 |
| previous_bookings_not_canceled | 0.000 | 3620 | 3.032 |
| booking_changes | 0.000 | 18076 | 15.140 |
| days_in_waiting_list | 0.000 | 3698 | 3.097 |
| required_car_parking_spaces | 0.000 | 7416 | 6.212 |
| total_of_special_requests | 1.000 | 2877 | 2.410 |

## City Hotel vs Resort Hotel Observations

The tables compare observed counts and within-hotel percentages. Differences are descriptive, do not rank data quality, do not establish causes, and do not demonstrate better performance from hotel-specific models.

| Hotel | Hotel records | Measure | Rows | Percentage within hotel |
| --- | --- | --- | --- | --- |
| City Hotel | 79330 | Any missing value | 79283 | 99.941 |
| City Hotel | 79330 | Duplicate copies | 25902 | 32.651 |
| City Hotel | 79330 | Duplicate involvement | 31748 | 40.020 |
| City Hotel | 79330 | Zero guests | 167 | 0.211 |
| City Hotel | 79330 | Zero stay | 331 | 0.417 |
| City Hotel | 79330 | Negative ADR | 0 | 0.000 |
| City Hotel | 79330 | Zero ADR | 1208 | 1.523 |
| Resort Hotel | 40060 | Any missing value | 39890 | 99.576 |
| Resort Hotel | 40060 | Duplicate copies | 6092 | 15.207 |
| Resort Hotel | 40060 | Duplicate involvement | 8417 | 21.011 |
| Resort Hotel | 40060 | Zero guests | 13 | 0.032 |
| Resort Hotel | 40060 | Zero stay | 384 | 0.959 |
| Resort Hotel | 40060 | Negative ADR | 1 | 0.002 |
| Resort Hotel | 40060 | Zero ADR | 751 | 1.875 |

Feature-specific missingness (denominator: records of that hotel):

| Hotel | Feature | Hotel records | Missing count | Missing percentage within hotel |
| --- | --- | --- | --- | --- |
| City Hotel | company | 79330 | 75641 | 95.350 |
| City Hotel | agent | 79330 | 8131 | 10.250 |
| City Hotel | country | 79330 | 24 | 0.030 |
| City Hotel | children | 79330 | 4 | 0.005 |
| Resort Hotel | company | 40060 | 36952 | 92.242 |
| Resort Hotel | agent | 40060 | 8209 | 20.492 |
| Resort Hotel | country | 40060 | 464 | 1.158 |
| Resort Hotel | children | 40060 | 0 | 0.000 |

## Decisions Pending for Preprocessing

- Investigate the meaning of missing values in the affected fields before choosing treatment.
- Establish whether identical full-row patterns are distinct bookings before considering duplicate removal.
- Clarify zero-guest, zero-stay, negative/zero ADR, and extreme-value records using context.
- Review IQR candidates in later EDA, particularly fields with IQR = 0.
- Verify detected context-label meanings in dataset documentation.
- Consider the observed hotel-specific patterns when justifying preprocessing decisions.
- Conduct the dedicated leakage audit separately; no features have been removed.

All treatment decisions will be justified during preprocessing. No rows, missing values, categories, or target values have been changed; no processed dataset, charts, or models were created.
