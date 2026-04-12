WITH source AS (
    SELECT * FROM raw.products
),

cleaned AS (
    SELECT
        product_id,
        TRIM(product_name)          AS product_name,
        UPPER(category)             AS category,
        subcategory,
        ROUND(unit_price, 2)        AS unit_price,
        ROUND(cost_price, 2)        AS cost_price,
        ROUND(unit_price - cost_price, 2) AS gross_margin,
        ROUND((unit_price - cost_price) / NULLIF(unit_price, 0) * 100, 2) AS margin_pct,
        stock_quantity,
        is_active,
        created_at
    FROM source
    WHERE product_id IS NOT NULL
      AND unit_price > 0
)

SELECT * FROM cleaned
