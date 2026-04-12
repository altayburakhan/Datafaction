WITH source AS (
    SELECT * FROM raw.customers
),

renamed AS (
    SELECT
        customer_id,
        first_name,
        last_name,
        first_name || ' ' || last_name AS full_name,
        LOWER(email)                   AS email,
        phone,
        city,
        UPPER(country)                 AS country_code,
        CAST(signup_date AS DATE)      AS signup_date,
        is_active,
        created_at
    FROM source
    WHERE customer_id IS NOT NULL
      AND email IS NOT NULL
)

SELECT * FROM renamed
