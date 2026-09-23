# Data Dictionary

Source: `data/raw/hotel_bookings.csv`, inspected in `notebooks/01_data_understanding.ipynb`. The table contains one row per observed column, in source order.

Data types are the observed pandas 3.0.3 CSV-inferred dtypes. Inference may differ across pandas versions; these types do not establish final semantic or modelling roles. Descriptions are conservative interpretations of names and project context, not a verified source codebook. Unconfirmed units, codes, and event definitions require dataset documentation.

All non-target roles are provisional. Leakage risk and preprocessing decisions remain pending; inclusion here does not establish suitability for prediction.

| Feature | Description | Data Type | Role | Leakage Risk | Preprocessing Decision |
|---|---|---|---|---|---|
| hotel | Hotel type recorded for the booking; central to the City Hotel versus Resort Hotel investigation. | str | Context / grouping feature | Pending leakage audit | Pending preprocessing analysis |
| is_canceled | Recorded cancellation outcome: 0 = Not Cancelled; 1 = Cancelled. | int64 | Target | N/A — target | Pending preprocessing analysis |
| lead_time | Booking lead time; exact interval definition and unit to be verified from dataset documentation. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| arrival_date_year | Year of the recorded arrival date. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| arrival_date_month | Month of the recorded arrival date. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| arrival_date_week_number | Week number of the recorded arrival date; week numbering convention requires verification. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| arrival_date_day_of_month | Day of the month of the recorded arrival date. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| stays_in_weekend_nights | Number of weekend nights recorded for the stay; weekend definition requires verification. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| stays_in_week_nights | Number of weekday nights recorded for the stay; weekday definition requires verification. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| adults | Number of adults recorded for the booking. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| children | Number of children recorded for the booking. | float64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| babies | Number of babies recorded for the booking. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| meal | Meal category recorded for the booking; category codes require verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| country | Country code recorded for the booking; exact interpretation and coding standard require verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| market_segment | Market segment recorded for the booking. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| distribution_channel | Distribution channel recorded for the booking. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| is_repeated_guest | Indicator of repeated-guest status; coding requires verification. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| previous_cancellations | Count of previous cancellations recorded for the guest. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| previous_bookings_not_canceled | Count of previous bookings recorded as not cancelled for the guest. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| reserved_room_type | Reserved room-type code; code meanings require verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| assigned_room_type | Assigned room-type code; code meanings require verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| booking_changes | Number of booking changes recorded; counting rules require verification. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| deposit_type | Deposit category recorded for the booking. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| agent | Agent-related code; identifier interpretation requires verification. | float64 | Identifier-like feature | Pending leakage audit | Pending preprocessing analysis |
| company | Company-related code; identifier interpretation requires verification. | float64 | Identifier-like feature | Pending leakage audit | Pending preprocessing analysis |
| days_in_waiting_list | Number of days recorded on a waiting list. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| customer_type | Customer category recorded for the booking. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| adr | To be verified from dataset documentation | float64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| required_car_parking_spaces | Number of car parking spaces requested for the booking. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| total_of_special_requests | Number of special requests recorded for the booking. | int64 | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| reservation_status | Recorded reservation status; status timing and definitions require verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
| reservation_status_date | Date associated with the recorded reservation status; exact event definition requires verification. | str | Candidate predictor | Pending leakage audit | Pending preprocessing analysis |
