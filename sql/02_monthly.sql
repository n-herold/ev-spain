SELECT year, month, COUNT(*) AS total, 
COUNT(*) FILTER (WHERE ev_category = 'BEV') AS bev
FROM registrations 
GROUP BY year, month
ORDER BY year, month;
