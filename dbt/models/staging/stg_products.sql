WITH source AS (
    SELECT * FROM raw.products
),

cleaned AS (
    SELECT
        product_id,
        TRIM(product_name)          AS product_name,
        category,
        subcategory,
        ROUND(unit_price, 2)        AS unit_price,
        ROUND(cost_price, 2)        AS cost_price,
        stock_quantity,
        is_active,
        created_at
    FROM source
    WHERE product_id IS NOT NULL
      AND unit_price > 0
)

SELECT * FROM cleaned
