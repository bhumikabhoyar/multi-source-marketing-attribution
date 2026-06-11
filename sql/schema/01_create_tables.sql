CREATE DATABASE IF NOT EXISTS marketing_db;
USE marketing_db;

CREATE TABLE IF NOT EXISTS customers (
    customer_id   INT            NOT NULL,
    signup_date   DATE           NOT NULL,
    segment       VARCHAR(20)    NOT NULL,
    country       VARCHAR(50)    NOT NULL,
    PRIMARY KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS touchpoints (
    touchpoint_id  INT             NOT NULL AUTO_INCREMENT,
    customer_id    INT             NOT NULL,
    channel        VARCHAR(30)     NOT NULL,
    campaign_name  VARCHAR(60)     NOT NULL,
    touch_date     DATETIME        NOT NULL,
    cost_inr       DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    PRIMARY KEY (touchpoint_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS conversions (
    conversion_id   INT             NOT NULL AUTO_INCREMENT,
    customer_id     INT             NOT NULL,
    conversion_date DATETIME        NOT NULL,
    revenue_inr     DECIMAL(10,2)   NOT NULL,
    PRIMARY KEY (conversion_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS ab_assignments (
    customer_id    INT          NOT NULL,
    test_group     VARCHAR(10)  NOT NULL,
    campaign_name  VARCHAR(60)  NOT NULL,
    PRIMARY KEY (customer_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);