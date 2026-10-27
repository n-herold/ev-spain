-- How many rows does the table have?
SELECT COUNT(*) AS rows_total FROM registrations;

-- New passenger cars per month
SELECT year, month, COUNT(*) AS cars
FROM registrations
GROUP BY year, month
ORDER BY year, month;
