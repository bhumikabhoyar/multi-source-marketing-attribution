USE marketing_db;

CREATE OR REPLACE VIEW vw_linear AS
WITH journey AS (
    SELECT
        t.customer_id,
        t.channel,
        t.campaign_name,
        t.touch_date,
        c.revenue_inr,
        COUNT(*) OVER (
            PARTITION BY t.customer_id
        ) AS touch_count
    FROM touchpoints t
    INNER JOIN conversions c
        ON  t.customer_id   = c.customer_id
        AND t.touch_date   <= c.conversion_date
)
SELECT
    channel,
    campaign_name,
    COUNT(DISTINCT customer_id)                    AS customers_reached,
    ROUND(SUM(revenue_inr / touch_count), 2)       AS attributed_revenue_inr,
    ROUND(AVG(revenue_inr / touch_count), 2)       AS avg_attributed_per_touch
FROM journey
GROUP BY channel, campaign_name
ORDER BY attributed_revenue_inr DESC;