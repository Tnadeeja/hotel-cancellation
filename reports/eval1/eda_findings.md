# Exploratory Data Analysis Findings

Source: `data/raw/hotel_bookings.csv`, 119,390 records × 32 columns. Calculated in `notebooks/03_exploratory_data_analysis.ipynb`. All results are descriptive, unadjusted, and based on raw records. No preprocessing or model development has been performed. Rates use within-group denominators; sample sizes are shown with comparisons.

## Target Distribution

Not Cancelled: 75,166 (62.96%); Cancelled: 44,224 (37.04%). The class distribution is not perfectly balanced. No resampling decision is made.

## City Hotel vs Resort Hotel

City Hotel: 41.73%; Resort Hotel: 27.76%. City minus Resort is 13.96 percentage points. This descriptive difference motivates hotel-specific investigation; it does not establish significance, causation, or model superiority.

| Hotel | Records | Cancellation rate (%) | Median lead time | Median ADR | Mean stay nights | Median stay nights | Repeated-guest proportion (%) | Mean special requests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| City Hotel | 79330 | 41.73 | 74.00 | 99.90 | 2.98 | 3.00 | 2.56 | 0.55 |
| Resort Hotel | 40060 | 27.76 | 57.00 | 75.00 | 4.32 | 3.00 | 4.44 | 0.62 |

City/Resort medians: lead time 74/57, ADR 99.90/75.00, stay 3/3 nights. Mean stay is 2.98/4.32 nights and repeated-guest share is 2.56%/4.44%. Mean special requests are comparatively close at 0.55/0.62. The cancellation-rate, lead-time, and stay differences support continuing hotel-specific investigation, but cannot predict whether separate models will outperform a general model.

## Important Cancellation Patterns

**Lead time:** Median lead time is 113 for Cancelled and 45 for Not Cancelled records. 1–7: 10.98% (n=13,401); 181–365: 55.45% (n=21,544). These are unadjusted associations.

**Arrival month:** Pooled monthly extremes: June: 41.46% (n=10,939); January: 30.48% (n=5,929). Observed months per year: 2015: 6; 2016: 12; 2017: 8. Unequal month coverage and hotel composition limit a seasonal interpretation.

**Customer history:** Not recorded as repeated: 37.79% (n=115,580); Recorded as repeated: 14.49% (n=3,810). Previous cancellations: ≤0: 33.91% (n=112,906); >0: 91.64% (n=6,484). Previous non-cancelled bookings: ≤0: 38.03% (n=115,770); >0: 5.52% (n=3,620).

**Customer type:** Among displayed categories with at least 100 records: Transient: 40.75% (n=89,613); Group: 10.23% (n=577). All categories contain at least 100 records.

**Market segment:** Among displayed categories with at least 100 records: Groups: 61.06% (n=19,811); Complementary: 13.06% (n=743). 1 small category/categories remain in the tables; their rates are sensitive to small counts.

**Deposit type:** Among displayed categories with at least 100 records: Non Refund: 99.36% (n=14,587); Refundable: 22.22% (n=162). All categories contain at least 100 records.

**Special requests:** 0: 47.72% (n=70,318); 1: 22.02% (n=33,226); 2: 22.10% (n=12,969). Request counts are associated with different observed rates; no causal interpretation is made.

**Stay length:** There are 715 zero-night records; none were removed. Median total stay: Cancelled 3, Not Cancelled 3. 1: 25.08% (n=21,020); 4–7: 35.90% (n=37,679).

**ADR:** ADR range -6.38–5400; median ADR for Cancelled 96.20, Not Cancelled 92.50. The zoom shows 0–252; 1,169 records outside it remain in all full-data calculations. This aggregate comparison does not adjust for hotel or arrival period.

## Data Quality Observations Reinforced by EDA

All 31,994 extra identical rows remain. Zero guests: 180; zero stays: 715; unknown guest totals: 4. ADR includes 1 negative and 1,959 zero values. No records have been cleaned or excluded from full-data summaries. Sparse categories and skewed distributions require contextual review; the earlier quality audit remains the detailed source.

## Implications for Preprocessing

- Review missingness, repeated rows, zero totals, and unusual ADR values before deciding any treatment.
- Assess skew and sparse groups in the context of later model requirements; no scaling, resampling, or category regrouping is approved here.
- Evaluate temporary lead-time, guest, and stay calculations as possible representations later; none has been added to the raw data.
- Account for incomplete annual coverage when investigating arrival patterns.
- Review feature timing separately, including reservation_status, reservation_status_date, assigned_room_type, booking_changes, and other timing-sensitive fields. No columns were removed.

## Implications for Project Novelty

City/Resort medians: lead time 74/57, ADR 99.90/75.00, stay 3/3 nights. Mean stay is 2.98/4.32 nights and repeated-guest share is 2.56%/4.44%. Mean special requests are comparatively close at 0.55/0.62. The cancellation-rate, lead-time, and stay differences support continuing hotel-specific investigation, but cannot predict whether separate models will outperform a general model. The observed differences justify continuing the proposed investigation; they do not establish statistical significance, causation, or a modelling advantage.

13 figures were generated locally under `reports/figures/` (Git-ignored). Tables retain small groups; extreme rates in those groups should not be overinterpreted.
