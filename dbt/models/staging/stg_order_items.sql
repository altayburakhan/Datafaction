WITH source AS (
    SELECT * FROM raw.order_items
),

cleaned AS (
    SELECT
        item_id,
        order_id,
        product_id,
        quantity,
        ROUND(unit_price, 2)    AS unit_price,
        ROUND(total_price, 2)   AS total_price,
        created_at
    FROM source
    WHERE item_id IS NOT NULL
      AND quantity > 0
      AND unit_price > 0
)

SELECT * FROM cleaned
