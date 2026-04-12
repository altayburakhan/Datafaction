-- This test should return zero rows: no negative prices allowed
SELECT *
FROM {{ ref('stg_order_items') }}
WHERE unit_price < 0
   OR total_price < 0
   OR quantity <= 0
