-- Wie viele Zeilen hat die Tabelle?
SELECT COUNT(*) AS rows_total FROM registrations;

-- Neue Pkw pro Monat
SELECT year, month, COUNT(*) AS cars
FROM registrations
GROUP BY year, month
ORDER BY year, month;
