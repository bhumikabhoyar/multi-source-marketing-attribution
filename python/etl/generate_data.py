import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_CUSTOMERS = 5000

CHANNELS = {
    'paid_search':      {'weight': 0.22, 'avg_cost': 180,  'cvr_boost': 0.18},
    'email':            {'weight': 0.20, 'avg_cost': 30,   'cvr_boost': 0.22},
    'organic_search':   {'weight': 0.18, 'avg_cost': 0,    'cvr_boost': 0.15},
    'social_paid':      {'weight': 0.16, 'avg_cost': 220,  'cvr_boost': 0.12},
    'social_organic':   {'weight': 0.10, 'avg_cost': 0,    'cvr_boost': 0.08},
    'direct':           {'weight': 0.08, 'avg_cost': 0,    'cvr_boost': 0.25},
    'referral':         {'weight': 0.06, 'avg_cost': 50,   'cvr_boost': 0.20},
}

CAMPAIGNS = {
    'paid_search':    ['brand_search_q1', 'competitor_kw', 'product_generic'],
    'email':          ['welcome_series',  'cart_abandon',  'reengagement'],
    'organic_search': ['seo_blog',        'seo_product',   'seo_category'],
    'social_paid':    ['fb_prospecting',  'ig_retarget',   'fb_lookalike'],
    'social_organic': ['ig_organic',      'linkedin_post', 'twitter_organic'],
    'direct':         ['direct_visit',    'bookmark',      'typed_url'],
    'referral':       ['partner_a',       'review_site',   'coupon_site'],
}

COUNTRIES  = ['India', 'India', 'India', 'USA', 'UK', 'UAE', 'Singapore']
SEGMENTS   = ['new', 'new', 'returning', 'returning', 'returning']

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        rows.append({
            'customer_id':  i,
            'signup_date':  random_date(START_DATE, END_DATE).date(),
            'segment':      random.choice(SEGMENTS),
            'country':      random.choice(COUNTRIES),
        })
    return pd.DataFrame(rows)

def generate_touchpoints(customers_df):
    rows = []
    tp_id = 1
    channel_names = list(CHANNELS.keys())
    channel_weights = [CHANNELS[c]['weight'] for c in channel_names]

    for _, cust in customers_df.iterrows():
        n_touches = np.random.choice([1,2,3,4,5,6], p=[0.20,0.25,0.22,0.17,0.10,0.06])
        base_date = random_date(START_DATE, END_DATE - timedelta(days=60))
        for j in range(n_touches):
            channel = random.choices(channel_names, weights=channel_weights, k=1)[0]
            campaign = random.choice(CAMPAIGNS[channel])
            avg_cost = CHANNELS[channel]['avg_cost']
            cost = round(max(0, np.random.normal(avg_cost, avg_cost * 0.3)), 2) if avg_cost > 0 else 0.0
            touch_dt = base_date + timedelta(days=j * random.randint(1, 14))
            rows.append({
                'touchpoint_id': tp_id,
                'customer_id':   cust['customer_id'],
                'channel':       channel,
                'campaign_name': campaign,
                'touch_date':    touch_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'cost_inr':      cost,
            })
            tp_id += 1
    return pd.DataFrame(rows)

def generate_conversions(customers_df, touchpoints_df):
    rows = []
    conv_id = 1
    last_touch = (
        touchpoints_df
        .sort_values('touch_date')
        .groupby('customer_id')
        .last()
        .reset_index()[['customer_id', 'channel', 'touch_date']]
    )
    for _, row in last_touch.iterrows():
        cvr_boost = CHANNELS[row['channel']]['cvr_boost']
        cust_segment = customers_df.loc[
            customers_df['customer_id'] == row['customer_id'], 'segment'
        ].values[0]
        base_prob = 0.55 if cust_segment == 'returning' else 0.45
        if random.random() < base_prob * (1 + cvr_boost):
            conv_date = pd.to_datetime(row['touch_date']) + timedelta(hours=random.randint(1, 72))
            if conv_date <= END_DATE:
                revenue = round(np.random.lognormal(mean=8.5, sigma=0.9), 2)
                rows.append({
                    'conversion_id':   conv_id,
                    'customer_id':     int(row['customer_id']),
                    'conversion_date': conv_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'revenue_inr':     revenue,
                })
                conv_id += 1
    return pd.DataFrame(rows)

def generate_ab_assignments(conversions_df, customers_df):
    # Use ~40% of customers who have at least one touchpoint
    eligible = customers_df['customer_id'].sample(frac=0.40, random_state=42)
    rows = []
    for cid in eligible:
        rows.append({
            'customer_id':   int(cid),
            'test_group':    random.choices(['control', 'variant'], weights=[0.5, 0.5])[0],
            'campaign_name': random.choice(['email_ab_q3', 'paid_ab_q3']),
        })
    df = pd.DataFrame(rows)
    # Inject a real lift for variant: bump conversion probability via revenue boost in post-processing
    return df

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    print("Generating customers...")
    customers = generate_customers()
    customers.to_csv('data/customers.csv', index=False)
    print(f"  {len(customers)} customers")

    print("Generating touchpoints...")
    touchpoints = generate_touchpoints(customers)
    touchpoints.to_csv('data/touchpoints.csv', index=False)
    print(f"  {len(touchpoints)} touchpoints")

    print("Generating conversions...")
    conversions = generate_conversions(customers, touchpoints)
    conversions.to_csv('data/conversions.csv', index=False)
    print(f"  {len(conversions)} conversions")

    print("Generating A/B assignments...")
    ab = generate_ab_assignments(conversions, customers)
    ab.to_csv('data/ab_assignments.csv', index=False)
    print(f"  {len(ab)} A/B assignments")

    print("\nSummary")
    print("-" * 38)
    print(f"Customers:       {len(customers):>6,}")
    print(f"Touchpoints:     {len(touchpoints):>6,}")
    print(f"Conversions:     {len(conversions):>6,}")
    print(f"A/B assignments: {len(ab):>6,}")
    cvr = len(conversions) / len(customers) * 100
    print(f"Overall CVR:     {cvr:>5.1f}%")
    print("\nChannel breakdown (touchpoints):")
    ch = touchpoints['channel'].value_counts()
    for c, n in ch.items():
        print(f"  {c:<20} {n:>6,}")
    print("\nFiles saved to ./data/")
