WITH daily AS (
    SELECT
        order_date_day                          AS date,
        order_year                              AS year,
        order_month                             AS month,
        COUNT(order_id)                         AS total_orders,
        COUNT(DISTINCT customer_id)             AS unique_customers,
        SUM(total_amount)                       AS gross_revenue,
        SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) AS net_revenue,
        SUM(CASE WHEN status = 'refunded' THEN total_amount ELSE 0 END)  AS refunded_amount,
        AVG(total_amount)                       AS avg_order_value,
        SUM(n_items)                            AS total_items_sold,
        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled_orders
    FROM {{ ref('int_orders_enriched') }}
    GROUP BY 1, 2, 3
),

with_growth AS (
    SELECT
        *,
        LAG(net_revenue) OVER (ORDER BY date) AS prev_day_revenue,
        ROUND(
            (net_revenue - LAG(net_revenue) OVER (ORDER BY date))
            / NULLIF(LAG(net_revenue) OVER (ORDER BY date), 0) * 100,
        2) AS revenue_growth_pct,
        ROUND(cancelled_orders * 100.0 / NULLIF(total_orders, 0), 2) AS cancellation_rate_pct
    FROM daily
)

SELECT * FROM with_growth
ORDER BY date DESC
