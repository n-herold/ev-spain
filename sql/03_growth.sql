WITH monthly AS (
    SELECT
        year,
        month,
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE ev_category = 'BEV') AS bev
    FROM registrations
    GROUP BY year, month
),
lagged AS (
    SELECT
        year,
        month,
        total,
        bev,
        LAG(bev, 1)  OVER (ORDER BY year, month) AS bev_prev_month,
        LAG(bev, 12) OVER (ORDER BY year, month) AS bev_prev_year
    FROM monthly
)
SELECT
    year,
    month,
    total,
    bev,
    ROUND(bev * 100.0 / total, 1) AS bev_share_pct,
    ROUND((bev - bev_prev_month) * 100.0 / bev_prev_month, 1) AS growth_mom_pct,
    ROUND((bev - bev_prev_year) * 100.0 / bev_prev_year, 1) AS growth_yoy_pct
FROM lagged
ORDER BY year, month;