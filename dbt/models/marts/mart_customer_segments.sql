-- RFM Analysis: Recency, Frequency, Monetary
WITH rfm_base AS (
    SELECT
        customer_id,
        MAX(order_date_day)                 AS last_order_date,
        CURRENT_DATE - MAX(order_date_day)          AS recency_days,
        COUNT(DISTINCT order_id)            AS frequency,
        SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) AS monetary
    FROM {{ ref('int_orders_enriched') }}
    GROUP BY customer_id
),

rfm_scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC)    AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC)     AS m_score
    FROM rfm_base
),

segmented AS (
    SELECT
        *,
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS rfm_avg,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential Loyalists'
        END AS segment
    FROM rfm_scored
)

SELECT
    s.*,
    c.full_name,
    c.country_code,
    c.signup_date
FROM segmented s
LEFT JOIN {{ ref('stg_customers') }} c USING (customer_id)
