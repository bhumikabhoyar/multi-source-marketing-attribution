USE marketing_db;

-- A. Journey length distribution
SELECT
    touch_count                             AS touches_before_conversion,
    COUNT(*)                                AS num_customers,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
    1)                                      AS pct_of_converters
FROM (
    SELECT
        t.customer_id,
        COUNT(*) AS touch_count
    FROM touchpoints t
    INNER JOIN conversions c
        ON  t.customer_id   = c.customer_id
        AND t.touch_date   <= c.conversion_date
    GROUP BY t.customer_id
) journey_lengths
GROUP BY touch_count
ORDER BY touch_count;

-- B. Average days first touch to conversion
SELECT
    cu.segment,
    ROUND(AVG(
        DATEDIFF(c.conversion_date, first_t.first_touch)
    ), 1)                                   AS avg_days_to_convert,
    COUNT(*)                                AS converters
FROM conversions c
JOIN customers cu ON c.customer_id = cu.customer_id
JOIN (
    SELECT customer_id, MIN(touch_date) AS first_touch
    FROM touchpoints
    GROUP BY customer_id
) first_t ON c.customer_id = first_t.customer_id
GROUP BY cu.segment;

-- C. Top 10 two-channel sequences
WITH first_last AS (
    SELECT
        ranked.customer_id,
        MIN(CASE WHEN rn_asc  = 1 THEN ranked.channel END)  AS entry_channel,
        MIN(CASE WHEN rn_desc = 1 THEN ranked.channel END)  AS exit_channel
    FROM (
        SELECT
            t2.customer_id, t2.channel,
            ROW_NUMBER() OVER (PARTITION BY t2.customer_id ORDER BY t2.touch_date ASC)  AS rn_asc,
            ROW_NUMBER() OVER (PARTITION BY t2.customer_id ORDER BY t2.touch_date DESC) AS rn_desc
        FROM touchpoints t2
        INNER JOIN conversions c ON t2.customer_id = c.customer_id
            AND t2.touch_date <= c.conversion_date
    ) ranked
    GROUP BY ranked.customer_id
)
SELECT
    CONCAT(entry_channel, ' → ', exit_channel)   AS journey_path,
    COUNT(*)                                      AS frequency
FROM first_last
WHERE entry_channel <> exit_channel
GROUP BY entry_channel, exit_channel
ORDER BY frequency DESC
LIMIT 10;