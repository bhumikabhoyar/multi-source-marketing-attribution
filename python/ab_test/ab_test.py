"""
ab_test.py
──────────
A/B test: Does the variant campaign convert better than control?
Two tests:
  1. Conversion rate  — two-proportion z-test
  2. Revenue per user — independent samples t-test

Run: python python/ab_test/ab_test.py
"""

import pandas as pd
import sqlalchemy
import urllib.parse
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest

# ─────────────────────────────────────────
# CONFIG — apna password aur path update karo
# ─────────────────────────────────────────
DB_USER     = "root"
DB_PASSWORD = "Bhumika@2026"       # ← apna MySQL password
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_NAME     = "marketing_db"
# ─────────────────────────────────────────

password = urllib.parse.quote_plus(DB_PASSWORD)
engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Data pull ────────────────────────────
df = pd.read_sql("""
    SELECT
        a.customer_id,
        a.test_group,
        a.campaign_name,
        CASE WHEN c.customer_id IS NOT NULL THEN 1 ELSE 0 END AS converted,
        COALESCE(c.revenue_inr, 0) AS revenue_inr
    FROM ab_assignments a
    LEFT JOIN conversions c ON a.customer_id = c.customer_id
""", engine)

print("=" * 50)
print("       A/B TEST RESULTS — MARKETING DB")
print("=" * 50)

# ── Group summary ────────────────────────
summary = df.groupby('test_group').agg(
    total_users   = ('customer_id', 'count'),
    conversions   = ('converted', 'sum'),
    total_revenue = ('revenue_inr', 'sum'),
).assign(
    cvr           = lambda x: x['conversions'] / x['total_users'] * 100,
    revenue_pu    = lambda x: x['total_revenue'] / x['total_users'],
)
print("\n── Group Summary ──")
print(summary.round(2).to_string())

# ── Test 1: Conversion Rate (z-test) ─────
control = df[df.test_group == 'control']
variant = df[df.test_group == 'variant']

counts = [variant['converted'].sum(), control['converted'].sum()]
nobs   = [len(variant), len(control)]
z_stat, p_cvr = proportions_ztest(counts, nobs)

cvr_control = control['converted'].mean() * 100
cvr_variant = variant['converted'].mean() * 100
lift_cvr    = (cvr_variant - cvr_control) / cvr_control * 100

print("\n── Test 1: Conversion Rate ──")
print(f"  Control CVR   : {cvr_control:.2f}%")
print(f"  Variant CVR   : {cvr_variant:.2f}%")
print(f"  Lift          : {lift_cvr:+.1f}%")
print(f"  Z-statistic   : {z_stat:.4f}")
print(f"  P-value       : {p_cvr:.4f}")
print(f"  Significant   : {'✅ YES (p < 0.05)' if p_cvr < 0.05 else '❌ NO (p >= 0.05)'}")

# ── Test 2: Revenue per User (t-test) ────
t_stat, p_rev = stats.ttest_ind(
    variant['revenue_inr'],
    control['revenue_inr'],
    equal_var=False   # Welch's t-test
)

rev_control = control['revenue_inr'].mean()
rev_variant = variant['revenue_inr'].mean()
lift_rev    = (rev_variant - rev_control) / rev_control * 100

print("\n── Test 2: Revenue Per User ──")
print(f"  Control RPU   : ₹{rev_control:,.2f}")
print(f"  Variant RPU   : ₹{rev_variant:,.2f}")
print(f"  Lift          : {lift_rev:+.1f}%")
print(f"  T-statistic   : {t_stat:.4f}")
print(f"  P-value       : {p_rev:.4f}")
print(f"  Significant   : {'✅ YES (p < 0.05)' if p_rev < 0.05 else '❌ NO (p >= 0.05)'}")

# ── Final Verdict ─────────────────────────
print("\n── Final Verdict ──")
if p_cvr < 0.05 and lift_cvr > 0:
    print("  🚀 Variant WINS — Roll out the variant campaign!")
elif p_cvr < 0.05 and lift_cvr < 0:
    print("  ⚠️  Control WINS — Variant is performing worse!")
else:
    print("  ⏳ No significant difference — Need more data.")

# ── Export for Power BI ───────────────────
export = pd.DataFrame([{
    'group':        'control',
    'users':        len(control),
    'conversions':  int(control['converted'].sum()),
    'cvr_pct':      round(cvr_control, 2),
    'avg_revenue':  round(rev_control, 2),
    'p_value_cvr':  round(p_cvr, 4),
    'significant':  'Yes' if p_cvr < 0.05 else 'No'
}, {
    'group':        'variant',
    'users':        len(variant),
    'conversions':  int(variant['converted'].sum()),
    'cvr_pct':      round(cvr_variant, 2),
    'avg_revenue':  round(rev_variant, 2),
    'p_value_cvr':  round(p_cvr, 4),
    'significant':  'Yes' if p_cvr < 0.05 else 'No'
}])

export.to_csv('data/ab_test_results.csv', index=False)
print("\n  📁 Exported: data/ab_test_results.csv (Power BI ke liye)")
print("=" * 50)