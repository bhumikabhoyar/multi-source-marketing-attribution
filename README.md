# Multi-Source Marketing Attribution Model

A full-stack data analytics project that simulates customer journeys across 7 marketing channels, builds 4 attribution models in SQL, validates campaign performance using statistical A/B testing, and visualises results in a 4-page Power BI executive dashboard.

---

## Tech Stack

| Layer | Tools | | Data Generation | Python, Pandas, NumPy | | Database | MySQL | | SQL | Window Functions, CTEs, Views | | Statistics | Python, SciPy, Statsmodels | | Visualisation | Power BI, DAX |

---

## Project Structure

```
Multi-Source Marketing Attribution Model/
├── data/
│   ├── customers.csv
│   ├── touchpoints.csv
│   ├── conversions.csv
│   ├── ab_assignments.csv
│   └── ab_test_results.csv
│
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_indexes.sql
│   ├── views/
│   │   ├── 03_first_touch.sql
│   │   ├── 04_last_touch.sql
│   │   ├── 05_linear.sql
│   │   ├── 06_time_decay.sql
│   │   └── 07_channel_roi.sql
│   └── queries/
│       ├── 08_funnel_dropoff.sql
│       └── 09_journey_length.sql
│
├── python/
│   ├── etl/
│   │   ├── generate_data.py
│   │   └── load_to_mysql.py
│   └── ab_test/
│       └── ab_test.py
│
└── README.md
```

---

## Dataset

Synthetic dataset simulating a full-year (2024) e-commerce customer journey across 7 channels:

| Table | Rows | Description |
|---|---|---|
| customers | 5,000 | Segment, country, signup date |
| touchpoints | 14,357 | Channel interactions with cost |
| conversions | 2,975 | Purchase events with revenue |
| ab_assignments | 2,000 | A/B test group assignments |

**Channels:** `paid_search` · `email` · `organic_search` · `social_paid` · `social_organic` · `direct` · `referral`

---

## Attribution Models

4 models built in SQL using window functions and CTEs:

**1. First-Touch** — 100% credit to the first channel the customer interacted with before converting.

**2. Last-Touch** — 100% credit to the last channel before conversion. Default in Google Analytics.

**3. Linear** — Revenue split equally across all touchpoints in the customer journey.

**4. Time-Decay** — Touchpoints closer to conversion get exponentially more credit using `EXP(-0.1 * days_before_conversion)`.

### Key Insight
`direct` and `email` are overvalued by last-touch attribution. Switching to linear redistributes credit back to `paid_search` and `social_paid` which warm up customers earlier in the journey.

---

## A/B Test Results

Tested whether the variant email/paid campaign converts better than control using:
- **Two-proportion z-test** for conversion rate
- **Welch's t-test** for revenue per user

| Metric | Control | Variant | Lift |
|---|---|---|---|
| Users | 1,008 | 992 | — |
| Conversions | 610 | 617 | — |
| CVR | 60.52% | 62.20% | +2.8% |
| Avg Revenue | ₹5,130 | ₹4,753 | -7.3% |
| P-value (CVR) | 0.44 | | ❌ Not significant |

**Verdict:** Variant shows slightly higher CVR but lower revenue per user. Neither result is statistically significant (p > 0.05). Recommendation — do not roll out variant, collect more data.

---

## Power BI Dashboard

4-page executive dashboard connected to MySQL via DirectQuery:

| Page | Content |
|---|---|
| Executive Overview | KPI cards, revenue by channel, conversion share |
| Attribution Comparison | First-touch vs last-touch vs linear vs time-decay |
| Channel ROI & Funnel | Scatter plot, waterfall ROI%, CPA table |
| A/B Test Results | CVR comparison, revenue per user, p-value card |

---

## Run Order

```bash
# Step 1 — Generate data (optional, CSVs already in data/)
python python/etl/generate_data.py

# Step 2 — Create schema in MySQL Workbench
# Run: sql/01_create_tables.sql

# Step 3 — Load data
python python/etl/load_to_mysql.py

# Step 4 — Add indexes in MySQL Workbench
# Run: sql/02_indexes.sql

# Step 5 — Create views in MySQL Workbench
# Run all files in sql/views/ (03 to 07)

# Step 6 — Run A/B test
python python/ab_test/ab_test.py
```

---

## Key Learnings

- Last-touch attribution over-credits `direct` channel — customers who convert directly were already warmed up by earlier paid channels
- Time-decay model using exponential decay formula gives most realistic credit distribution
- A/B test shows variant has higher CVR but lower revenue — optimising for CVR alone can hurt revenue
- SQL window functions (`ROW_NUMBER`, `SUM OVER PARTITION`) are essential for multi-touch attribution logic
