SELECT year, COUNT(*) AS n_rows, ROUND(SUM(gwh), 1) AS total_gwh
FROM generation
GROUP BY year
ORDER BY year;
