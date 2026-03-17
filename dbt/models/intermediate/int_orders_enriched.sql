WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT customer_id, full_name, country_code, signup_date
    FROM {{ ref('stg_customers') }}
),

items_agg AS (
    SELECT
        order_id,
        COUNT(*)          AS n_items,
        SUM(quantity)     AS total_qty,
        SUM(total_price)  AS items_total
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
),

enriched AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.full_name        AS customer_name,
        c.country_code,
        c.signup_date,
        o.order_date,
        o.order_date_day,
        o.order_year,
        o.order_month,
        o.order_dow,
        o.status,
        o.total_amount,
        o.discount_pct,
        ia.n_items,
        ia.total_qty,
        DATEDIFF('day', c.signup_date, o.order_date_day) AS days_since_signup
    FROM orders o
    LEFT JOIN customers c USING (customer_id)
    LEFT JOIN items_agg ia USING (order_id)
)

SELECT * FROM enriched
