USE marketing_db;

CREATE OR REPLACE VIEW vw_channel_roi AS
WITH spend AS (
    SELECT
        channel,
        SUM(cost_inr)           AS total_spend_inr,
        COUNT(*)                AS total_touchpoints
    FROM touchpoints
    GROUP BY channel
),
revenue AS (
    SELECT
        channel,
        SUM(attributed_revenue_inr)  AS attributed_revenue_inr,
        SUM(customers_reached)       AS customers_reached
    FROM vw_linear
    GROUP BY channel
),
conversions_agg AS (
    SELECT
        lt.channel,
        COUNT(DISTINCT lt.customer_id)  AS total_conversions
    FROM (
        SELECT t.customer_id, t.channel
        FROM touchpoints t
        INNER JOIN conversions c
            ON  t.customer_id   = c.customer_id
            AND t.touch_date   <= c.conversion_date
    ) lt
    GROUP BY lt.channel
)
SELECT
    s.channel,
    ROUND(s.total_spend_inr, 2)                             AS total_spend_inr,
    ROUND(r.attributed_revenue_inr, 2)                      AS attributed_revenue_inr,
    ROUND(
        (r.attributed_revenue_inr - s.total_spend_inr)
        / NULLIF(s.total_spend_inr, 0) * 100,
    1)                                                      AS roi_pct,
    ROUND(
        s.total_spend_inr / NULLIF(ca.total_conversions, 0),
    2)                                                      AS cost_per_acquisition_inr,
    ca.total_conversions,
    s.total_touchpoints
FROM spend s
LEFT JOIN revenue          r  ON s.channel = r.channel
LEFT JOIN conversions_agg  ca ON s.channel = ca.channel
ORDER BY roi_pct DESC;