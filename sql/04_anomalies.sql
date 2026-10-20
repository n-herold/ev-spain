WITH monthly AS (
    SELECT
        year,
        month,
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE ev_category = 'BEV') AS bev
    FROM registrations
    GROUP BY year, month
),
shares AS (
    SELECT
        year,
        month,
        bev,
        bev * 100.0 / total AS share
    FROM monthly
),
baseline AS (
    SELECT
        year,
        month,
        bev,
        share,
        AVG(share)    OVER w AS base_avg,
        STDDEV(share) OVER w AS base_std
    FROM shares
    WINDOW w AS (
        ORDER BY year, month
        ROWS BETWEEN 6 PRECEDING AND 6 FOLLOWING EXCLUDE CURRENT ROW
    )
)
SELECT
    year,
    month,
    bev,
    ROUND(share, 1) AS share_pct,
    ROUND(base_avg, 1) AS base_pct,
    ROUND(share - base_avg, 1) AS diff_pp,
    ROUND((share - base_avg) / base_std, 1) AS z_score
FROM baseline
ORDER BY year, month;