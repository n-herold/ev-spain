WITH grouped AS (
    SELECT year, month, gwh,
        CASE
            WHEN technology IN ('Hidráulica', 'Eólica', 'Solar fotovoltaica', 'Solar térmica',
                                'Otras renovables', 'Residuos renovables', 'Hidroeólica') THEN 'Renewable'
            WHEN technology = 'Nuclear' THEN 'Nuclear'
            ELSE 'Fossil'
        END AS grp
    FROM generation
),
monthly AS (
    SELECT year, month, grp, SUM(gwh) AS gwh
    FROM grouped
    GROUP BY year, month, grp
),
shares AS (
    SELECT year, month, grp, gwh,
        gwh * 100.0 / SUM(gwh) OVER (PARTITION BY year, month) AS share
    FROM monthly
)
SELECT year, month, grp, ROUND(gwh, 1) AS gwh, ROUND(share, 1) AS share_pct
FROM shares
ORDER BY year, month, grp;
