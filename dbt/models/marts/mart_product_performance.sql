WITH items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

orders AS (
    SELECT order_id, status FROM {{ ref('stg_orders') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

agg AS (
    SELECT
        i.product_id,
        COUNT(DISTINCT i.order_id)                          AS total_orders,
        SUM(i.quantity)                                     AS units_sold,
        SUM(i.total_price)                                  AS gross_revenue,
        SUM(CASE WHEN o.status = 'completed' THEN i.total_price ELSE 0 END) AS net_revenue,
        SUM(CASE WHEN o.status = 'refunded' THEN 1 ELSE 0 END)             AS refund_count,
        AVG(i.unit_price)                                   AS avg_selling_price
    FROM items i
    LEFT JOIN orders o USING (order_id)
    GROUP BY i.product_id
)

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.unit_price          AS list_price,
    p.cost_price,
    p.margin_pct,
    a.total_orders,
    a.units_sold,
    a.gross_revenue,
    a.net_revenue,
    a.refund_count,
    ROUND(a.refund_count * 100.0 / NULLIF(a.total_orders, 0), 2) AS refund_rate_pct,
    a.avg_selling_price,
    ROUND(a.net_revenue - (p.cost_price * a.units_sold), 2) AS gross_profit
FROM products p
LEFT JOIN agg a USING (product_id)
ORDER BY a.net_revenue DESC NULLS LAST
