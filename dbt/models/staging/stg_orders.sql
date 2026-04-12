WITH source AS (
    SELECT * FROM raw.orders
),

cleaned AS (
    SELECT
        order_id,
        customer_id,
        CAST(order_date AS TIMESTAMP) AS order_date,
        CAST(order_date AS DATE)      AS order_date_day,
        EXTRACT(YEAR FROM order_date) AS order_year,
        EXTRACT(MONTH FROM order_date) AS order_month,
        EXTRACT(DOW FROM order_date)  AS order_dow,
        LOWER(status)                 AS status,
        shipping_city,
        shipping_country,
        ROUND(total_amount, 2)        AS total_amount,
        discount_pct,
        created_at
    FROM source
    WHERE order_id IS NOT NULL
      AND customer_id IS NOT NULL
      AND total_amount >= 0
)

SELECT * FROM cleaned
