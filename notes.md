Q1:

How did new BEV registrations in Spain develop (Jan 2023 - Sep 2026),

and are there anomalies that can be linked to events?



Data from: Spanish new-car registrations, prepared as Parquet files

(data/processed). Only BEV is analysed.



1. Getting and preparing the data

 - download script and prepare script (commits "download", "prepare")

 - result: Parquet files with year, month, ev_category



2. Creating run_sql.py

 - sets up DuckDB and the view "registrations"

 - runs the SQL file named in SQL_FILE and prints each result



3. Exploring (01_explore.sql and monthly query)

 - total registrations and BEV registrations per month

 - BEV share in % of all registrations



4. Growth (03_growth.sql)

 - CTE "monthly", then LAG(1) and LAG(12) for the previous month and year

 - month-on-month and year-on-year growth in %, plus BEV share



5. Anomalies (04_anomalies.sql)

 - baseline = average of the 6 months before and after (current month excluded)

 - z-score = (share - baseline) / standard deviation of the baseline



6. Plotting (04_plot.py)

 - monthly and cumulative values, cumulative by year, share vs baseline with z-scores

 - figures are saved in figures/



Results (descriptive, interpretation comes after all questions):

 - Sep 2024: 6,392 BEV, MoM +132.5 %, z = 2.0

 - Sep 2025: z = 2.1, Sep 2026: z = 4.9, Nov 2023: z = 2.4

 - no clear break after end of Feb 2026



Limitations:

 - first and last 6 months have truncated windows (edge effect), so

   the z = 4.9 in Sep 2026 is probably overstated

 - causes of the September peaks are not proven

 - event dates (Hormuz, subsidies) are still to be verified









----------------------------------------------------------------------------------------------------------------------------



Q2:

How did the charging infrastructure for e-cars in Spain change?



Data from: EAFO (European Alternative Fuels Observatory), public charging

points in Spain, quarterly, AC and DC. EAFO uses Eco-Movement data, not

official statistics.



1. Choosing the source

 - AEDIVE rejected: press-only data, restated end of 2024, different

   counting method in 2026

 - EAFO chosen: complete quarterly series, one consistent source

 - no source found for private chargers (data gap)



2. Preparing the data

 - exported EAFO table, saved as q2/data/eafo_charging_points.csv

 - columns: year, quarter, ac, dc (2023Q1 - 2026Q3)

 - one row from 2022Q4 is needed for the first quarter-on-quarter value



3. Creating run_q2.py

 - registers the CSV in DuckDB via pandas (DuckDB's own CSV reader failed)

 - runs the SQL file named in SQL_FILE



4. Quarterly change (01_quarterly.sql)

 - CTEs: base (AC + DC = total), lagged (LAG 1 quarter), pct

 - quarter-on-quarter change in % for AC, DC and total



5. Plotting (plot_q2.py)

 - top: stacked bars AC + DC per quarter

 - bottom: QoQ % lines for AC, DC, total

 - saved in q2/figures/



Results (descriptive):

 - total about 30.4k public points end of 2023, 49.8k in 2026Q3 (peak 53.0k in 2026Q2)

 - AC jumps by almost 10,000 in 2024Q4, probably a counting change

 - AC falls in 2024Q1, 2025Q1 and 2026Q3, DC rises steadily



Limitations:

 - quarterly, not monthly

 - QoQ is a net change, not new builds

 - only public points





------------------------------------------------------------------------------------------------------



Q3:



Where does all the power in Spain come from?



and where for the cars?





Plan:

1. Figure out where the power in Spain Comes from Overall in percentiles. (which countries)
2. What Kind of Energy is it?
* Solar, Nuclear ...? in percentiles



What Kind of Datasets to use:



REData-API (REE): https://www.ree.es/en/apidatos





Conclusion:

* mot of spains Energy is selfproduced







SO we look at how Spain produces this energy,leaving imports out for now !!!



Data from: REE

1. Downloaded data for the interested timespan (januar 23 - September 26)
* downloaded the data in Ghw and percent since available



2. Preparing the data

* prepare_q3.py for preparing the data for SQL
* running python code prepare_q3.py (coded by claude)

 - translating and formating the data table



3. Creating run_q3.py and check.sql



* run_q2 for carrying out the SQL code
* check to see if the py can really connectto the databank



4. Grouping by Renewable, Nuclear, Fossil

* creating 02_groups





5. Plotting the groupped data with plot_q3.py





