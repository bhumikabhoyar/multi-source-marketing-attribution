USE marketing_db;

CREATE INDEX idx_tp_customer_date  ON touchpoints (customer_id, touch_date(50));
CREATE INDEX idx_tp_channel        ON touchpoints (channel(30));
CREATE INDEX idx_tp_campaign       ON touchpoints (campaign_name(60));

CREATE INDEX idx_conv_date         ON conversions (conversion_date(50));

CREATE INDEX idx_cust_segment      ON customers (segment(20));
CREATE INDEX idx_cust_country      ON customers (country(50));

CREATE INDEX idx_ab_group          ON ab_assignments (test_group(10));
CREATE INDEX idx_ab_campaign       ON ab_assignments (campaign_name(60));