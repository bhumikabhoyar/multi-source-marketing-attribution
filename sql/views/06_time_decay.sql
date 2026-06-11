USE marketing_db;

CREATE OR REPLACE VIEW vw_time_decay AS
WITH journey AS (
    SELECT
        t.customer_id,
        t.channel,
        t.campaign_name,
        t.touch_date,
        c.conversion_date,
        c.revenue_inr,
        DATEDIFF(c.conversion_date, t.touch_date)  AS days_before_conv
    FROM touchpoints t
    INNER JOIN conversions c
        ON  t.customer_id   = c.customer_id
        AND t.touch_date   <= c.conversion_date
),
weighted AS (
    SELECT
        customer_id,
        channel,
        campaign_name,
        revenue_inr,
        EXP(-0.1 * days_before_conv)               AS decay_weight,
        SUM(EXP(-0.1 * days_before_conv)) OVER (
            PARTITION BY customer_id
        )                                          AS total_weight
    FROM journey
)
SELECT
    channel,
    campaign_name,
    COUNT(DISTINCT customer_id)                             AS customers_reached,
    ROUND(
        SUM(revenue_inr * decay_weight / total_weight), 2
    )                                                       AS attributed_revenue_inr,
    ROUND(
        AVG(revenue_inr * decay_weight / total_weight), 2
    )                                                       AS avg_attributed_per_touch
FROM weighted
GROUP BY channel, campaign_name
ORDER BY attributed_revenue_inr DESC;