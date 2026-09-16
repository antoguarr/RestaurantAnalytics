# SQL Analysis

This folder adds a small SQL component to the restaurant analytics project.

The SQL analysis uses SQLite against the cleaned Power BI export:

```text
powerbi/data/restaurant_pos_powerbi.csv
```

Each row is treated as a POS menu-item record. The source has no order or receipt ID, so SQL outputs report POS record counts and average line revenue rather than completed transactions or average order value.

## Files

```text
sql/
├── README.md
├── restaurant_analysis.sql
└── results/
    ├── average_daily_revenue_by_weekday.csv
    ├── dessert_upsell_by_server.csv
    ├── revenue_by_category.csv
    ├── revenue_by_hour.csv
    ├── server_performance.csv
    └── top_menu_items.csv
```

## How to Run

Refresh the Power BI-ready dataset first:

```bash
python scripts/export_powerbi_data.py
```

Then run the SQL analysis:

```bash
python scripts/run_sql_analysis.py
```

The script loads the CSV into an in-memory SQLite database, runs the queries from `restaurant_analysis.sql`, and exports the result tables to `sql/results/`.

## Included SQL Questions

- Which menu categories generate the most revenue?
- Which menu items are the top revenue drivers?
- Which weekdays have the highest average daily revenue?
- Which hours generate the most revenue?
- Which servers generate the most revenue and average line revenue?
- Which servers have the highest dessert revenue share?
