USE marketing_db;

CREATE OR REPLACE VIEW vw_last_touch AS
WITH ranked_touches AS (
    SELECT
        t.customer_id,
        t.channel,
        t.campaign_name,
        t.touch_date,
        ROW_NUMBER() OVER (
            PARTITION BY t.customer_id
            ORDER BY t.touch_date DESC
        ) AS rn
    FROM touchpoints t
    INNER JOIN conversions c
        ON  t.customer_id   = c.customer_id
        AND t.touch_date   <= c.conversion_date
),
last_touches AS (
    SELECT customer_id, channel, campaign_name
    FROM   ranked_touches
    WHERE  rn = 1
)
SELECT
    lt.channel,
    lt.campaign_name,
    COUNT(DISTINCT lt.customer_id)   AS conversions,
    SUM(c.revenue_inr)               AS attributed_revenue_inr,
    ROUND(AVG(c.revenue_inr), 2)     AS avg_order_value_inr
FROM last_touches lt
JOIN conversions c ON lt.customer_id = c.customer_id
GROUP BY lt.channel, lt.campaign_name
ORDER BY attributed_revenue_inr DESC;