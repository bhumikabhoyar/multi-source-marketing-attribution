USE marketing_db;

SELECT
    t.channel,
    COUNT(DISTINCT t.customer_id)                               AS total_touched,
    COUNT(DISTINCT c.customer_id)                               AS total_converted,
    COUNT(DISTINCT t.customer_id)
        - COUNT(DISTINCT c.customer_id)                         AS total_dropped,
    ROUND(
        COUNT(DISTINCT c.customer_id) * 100.0
        / NULLIF(COUNT(DISTINCT t.customer_id), 0),
    1)                                                          AS conversion_rate_pct,
    ROUND(
        AVG(touch_counts.n_touches), 1
    )                                                           AS avg_touches_to_convert
FROM touchpoints t
LEFT JOIN conversions c
    ON t.customer_id = c.customer_id
LEFT JOIN (
    SELECT
        tp.customer_id,
        COUNT(*) AS n_touches
    FROM touchpoints tp
    INNER JOIN conversions cv ON tp.customer_id = cv.customer_id
    WHERE tp.touch_date <= cv.conversion_date
    GROUP BY tp.customer_id
) touch_counts ON t.customer_id = touch_counts.customer_id
GROUP BY t.channel
ORDER BY conversion_rate_pct DESC;