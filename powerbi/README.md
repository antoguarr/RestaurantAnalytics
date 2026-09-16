# Power BI Report Guide

This folder contains the Power BI-ready version of the restaurant POS analytics project.

## Files

```text
powerbi/
├── README.md
├── dax_measures.md
└── data/
    └── restaurant_pos_powerbi.csv
```

## Dataset

Import this file into Power BI:

```text
powerbi/data/restaurant_pos_powerbi.csv
```

This file is generated from the original Kaggle POS dataset using:

```bash
python scripts/export_powerbi_data.py
```

The exported dataset includes cleaned fields and additional features:

- `hour`
- `weekday`
- `month_number`
- `month_name`
- `day_of_week`
- `is_weekend`
- `high_revenue`

Each row is one POS menu-item record. Because the source has no order or receipt ID, the report uses POS record count and average line revenue; it does not claim to measure completed orders or check-level average order value.

## Recommended Report Pages

### 1. Executive Overview

Purpose: Give stakeholders a quick summary of overall restaurant performance.

Recommended visuals:

- KPI cards:
  - Total Revenue
  - POS Records
  - Average Line Revenue
  - Units Sold
- Bar chart: Revenue by Category
- Bar chart: Revenue by Weekday
- Line chart: Revenue by Hour
- Slicers:
  - Date
  - Category
  - Server Name
  - Order Type
  - Payment Method

### 2. Menu Performance

Purpose: Show which menu items and categories drive sales.

Recommended visuals:

- Bar chart: Top 10 Menu Items by Revenue
- Donut chart: Revenue Share by Category
- Table:
  - Menu Item
  - Category
  - Total Revenue
  - Units Sold
  - Average Line Revenue
- Optional bar chart: Quantity Sold by Menu Item

### 3. Operations and Server Performance

Purpose: Compare staff and ordering channels.

Recommended visuals:

- Bar chart: Revenue by Server Name
- Bar chart: Average Line Revenue by Server Name
- Bar chart: Revenue by Order Type
- Bar chart: Revenue by Payment Method
- Matrix:
  - Rows: Server Name
  - Columns: Category
  - Values: Total Revenue or Units Sold

### 4. Insights and Recommendations

Purpose: Translate the analysis into business actions.

Recommended content:

| Finding | Recommendation |
| --- | --- |
| Entrees generated $272,974.90, about 62.0% of total revenue. | Prioritize entree inventory, premium steak promotion, and entree pairing offers. |
| Desserts represented $17,739.00, about 4.0% of total revenue. | Test dessert upselling prompts or bundles and measure their effect. |
| New York Strip, Filet Mignon, and Ribeye Steak generated $228,576.70 combined, about 51.9% of revenue. | Protect availability of top steak items and promote beverage or side pairings. |
| Saturday had the highest average daily revenue at about $1,421.85. | Increase staffing and prep levels for Saturday service. |
| 7 PM, 8 PM, and 9 PM were the strongest revenue hours. | Schedule experienced servers and kitchen coverage during peak dinner hours. |
| Nina led server revenue with $91,506.80, about 20.8% of total revenue. | Study top-server POS record patterns to form testable training hypotheses. |

## Suggested Power BI Workflow

1. Open Power BI Desktop.
2. Select **Get Data**.
3. Choose **Text/CSV**.
4. Import `powerbi/data/restaurant_pos_powerbi.csv`.
5. In Power Query, confirm:
   - `date` is Date
   - `time` is Time
   - `revenue`, `quantity`, and `price_per_item` are Decimal number
   - `server_id`, `hour`, `month_number`, and `day_of_week` are Whole number
   - `is_weekend` and `high_revenue` are True/False
6. Rename the table to `POS`.
7. Add the measures from `dax_measures.md`.
8. Build the report pages listed above.
9. Save the report as:

```text
powerbi/Restaurant_POS_Dashboard.pbix
```

10. Export the finished report as a PDF and save it as:

```text
powerbi/Restaurant_POS_Dashboard.pdf
```

## CV Positioning

After creating the report, this project can be described as:

> Built an end-to-end restaurant POS analytics project using Python, SQL, Streamlit, Power BI, and scikit-learn to analyze 5,000 Kaggle POS records, identify revenue patterns, compare model baselines, and communicate business recommendations through interactive dashboards.
