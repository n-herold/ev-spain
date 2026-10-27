\# Electric Cars in Spain: Registrations, Charging Infrastructure and Electricity Mix



A data analysis project with Python, DuckDB and SQL (January 2023 - September 2026).



\## 1. Introduction



Battery-electric vehicles (BEV) are becoming more common in Spain. In this project I look at three

parts of this development: how many BEVs are registered, how many public charging points exist, and

where the electricity comes from that these cars use. The aim is to describe all three in one

picture, to find unusual months and, where possible, to link them to events such as subsidy changes

or the Strait of Hormuz crisis.



\## 2. Research Questions



\- \*\*Q1:\*\* How did new BEV registrations in Spain develop between January 2023 and September 2026,

&#x20; and can anomalies be linked to events?

\- \*\*Q2:\*\* How did the number of public charging points for electric cars in Spain change over the

&#x20; same period?

\- \*\*Q3:\*\* Where does the electricity in Spain come from, i.e. how is it generated

&#x20; (renewable, nuclear, fossil)?



\## 3. Data



| Question | Source | Content | Frequency |

|----------|--------|---------|-----------|

| Q1 | DGT microdata | Registrations of new passenger cars | Monthly |

| Q2 | EAFO (European Alternative Fuels Observatory) | Public charging points, AC and DC | Quarterly |

| Q3 | REE (REData) | Electricity generation by technology in GWh | Monthly |



\- Retrieval dates and the sources used for the context research are listed in

&#x20; \[interpretation.md](interpretation.md).

\- REE data may be used with a source reference, but not for commercial or advertising purposes.



\## 4. Methodology



\*\*Q1: Registrations\*\*

1\. Download the monthly DGT files and keep new passenger cars (stored as Parquet).

2\. Calculate the monthly BEV share and the growth rates (month on month, year on year) with SQL.

3\. Detect anomalies with a z-score: each month is compared with the average of the six months before

&#x20;  and after it. Months with |z| >= 2 are flagged.



\*\*Q2: Charging points\*\*

1\. Use the quarterly EAFO figures for AC and DC points.

2\. Calculate the change versus the previous quarter for AC, DC and the total.



\*\*Q3: Electricity mix\*\*

1\. Clean the REE export (encoding, decimal comma, wide to long format) with Python.

2\. Group the technologies into renewable, nuclear and fossil.

3\. Calculate the monthly share of each group in total generation.



\## 5. Results



\### Q1: Registrations

\- The BEV share rose from 5.3 % (January 2023) to 18.7 % (September 2026).

\- Four months are flagged as anomalies: November 2023 (z = 2.4), September 2024 (z = 2.0),

&#x20; September 2025 (z = 2.1) and September 2026 (z = 4.9).

\- The strong year-on-year peak in August 2025 (+160.9 %) is a base effect of a weak August 2024.



!\[BEV share and anomalies](q1/figures/bev\_anomalies.png)



\### Q2: Charging points

\- Public charging points grew from about 23,400 (2023 Q1) to a peak of about 53,000 (2026 Q2).

\- DC points grew in almost every quarter, AC points fluctuated.

\- AC points jumped by 38.2 % in 2024 Q4.



!\[Public charging points](q2/figures/charging\_points\_quarterly.png)



\### Q3: Electricity mix

\- Renewables supplied the largest share in every month (42 % to 66 %).

\- Nuclear stayed between 15 % and 23 %, fossil sources between 17 % and 35 %.

\- The pattern is seasonal: renewables peak in spring, fossil sources rise in late summer and autumn.



!\[Electricity mix](q3/figures/generation\_groups\_monthly.png)



\## 6. Discussion



\- Three of the four anomalies in Q1 coincide with subsidy policy: the announced end of MOVES III

&#x20; (September 2024), the funds running out in several regions (September 2025) and the start of

&#x20; Plan Auto+ (September 2026). November 2023 was attributed to a record month for Tesla.

\- No break is visible after the start of the Strait of Hormuz crisis (28 February 2026).

\- The 2024 Q4 jump in AC points is probably a change in counting, not new construction, because

&#x20; another source reported only about 3,300 new points in that quarter.

\- Registrations grew much faster than the public charging network, while the electricity mix stayed

&#x20; roughly constant.



\## 7. Conclusion



BEV registrations in Spain grew strongly. Their anomalies can plausibly be linked to changes in

subsidy policy rather than to infrastructure or electricity supply. The public charging network

roughly doubled, but two of its largest movements are data effects. The electricity mix was already

largely low-carbon in 2023 and did not improve measurably within the period. The Strait of Hormuz

crisis left no visible mark on any of the three series.



The full analysis is in \[interpretation.md](interpretation.md), my working notes are in

\[notes.md](notes.md).



\## 8. Limitations



\- Links between events and anomalies are associations, not proof of causation.

\- The baseline of the z-score uses truncated windows at the start and end of the series, so the value

&#x20; for September 2026 is probably overstated.

\- Only public charging points are included, and the EAFO figures are not official statistics.

\- The quarter-on-quarter change is a net change in the stock, not the number of newly built points.

\- Electricity cannot be traced to a single power plant, so the mix applies statistically to the whole grid.

\- Q2 is quarterly, Q1 and Q3 are monthly, so the series cannot be compared month by month.



\## 9. Project Structure and Reproducibility



```

q1/   registrations: scripts, sql, figures (raw data is not in the repository)

q2/   charging points: scripts, sql, figures, data

q3/   electricity mix: scripts, sql, figures, data

interpretation.md   joint analysis, limitations, sources

notes.md            working notes per question

```



Requirements: Python 3 with `duckdb`, `pandas`, `matplotlib`, `pyarrow` and `requests`.



| Question | Order of the scripts |

|----------|----------------------|

| Q1 | `01\_download.py` (several hundred MB), `02\_prepare.py`, `run\_sql.py` (set `SQL\_FILE`), `04\_plot.py` |

| Q2 | `run\_q2.py`, `plot\_q2.py` |

| Q3 | `prepare\_q3.py`, `run\_q3.py`, `plot\_q3.py` |



\## 10. References



See the source list in \[interpretation.md](interpretation.md).

