WITH base AS (
    SELECT
        year,
        quarter,
        ac,
        dc,
        ac + dc AS total
    FROM charging_points
),
lagged AS (
    SELECT
        year,
        quarter,
        ac,
        dc,
        total,
        LAG(ac, 1)    OVER w AS ac_prev,
        LAG(dc, 1)    OVER w AS dc_prev,
        LAG(total, 1) OVER w AS total_prev
    FROM base
    WINDOW w AS (ORDER BY year, quarter)
),
pct AS (
    SELECT
        year,
        quarter,
        ac,
        dc,
        total,
        ROUND((ac - ac_prev) * 100.0 / ac_prev, 1)          AS ac_qoq_pct,
        ROUND((dc - dc_prev) * 100.0 / dc_prev, 1)          AS dc_qoq_pct,
        ROUND((total - total_prev) * 100.0 / total_prev, 1) AS total_qoq_pct
    FROM lagged
)
SELECT
    year,
    quarter,
    ac,
    dc,
    total,
    ac_qoq_pct,
    dc_qoq_pct,
    total_qoq_pct
FROM pct
WHERE year >= 2023
ORDER BY year, quarter;
