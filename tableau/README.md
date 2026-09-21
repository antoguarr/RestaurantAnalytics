# Tableau Dashboard Guide

This folder is the Tableau reporting layer for the restaurant POS analytics project. It contains a ready-to-import workbook, reproducible CSV sources, calculated fields, and a precise dashboard build specification.

![Executive overview preview](screenshots/tableau-executive-overview.png)

## Files

```text
tableau/
├── README.md
├── calculated_fields.md
├── data/
│   ├── model_results.csv
│   ├── pos_records.csv
│   ├── restaurant_pos_tableau.xlsx
│   └── staffing_schedule.csv
└── screenshots/
    ├── tableau-executive-overview.png
    └── tableau-staffing-models.png
```

## Data Source

Open `data/restaurant_pos_tableau.xlsx` in Tableau. It contains four sheets:

| Sheet | Grain | Purpose |
| --- | --- | --- |
| `POS Records` | One row per menu-item POS record | Revenue, menu, time, channel, and server analysis |
| `Staffing Schedule` | One row per weekday-hour combination | Predicted staffing-demand heatmap and recommendations |
| `Model Results` | One row per model and prediction task | Baseline, Logistic Regression, and Random Forest comparison |
| `Data Dictionary` | One row per important field | Definitions, types, and analytical limitations |

The source has no receipt or order ID. Do not label record counts as orders or transactions, and do not label average line revenue as average order value.

## Dashboard 1: Executive Overview

Use a fixed desktop size of `1200 x 800` and tiled containers.

### Header and filters

- Title: `Restaurant POS Executive Overview`
- Filters: Date, Category, Server Name, Order Type, Payment Method
- Apply each filter to all worksheets using the `POS Records` data source.

### KPI row

Create four text worksheets using the calculated fields in `calculated_fields.md`:

- Total Revenue
- POS Records
- Average Line Revenue
- Units Sold

### Main views

| View | Columns | Rows | Marks / notes |
| --- | --- | --- | --- |
| Revenue by Category | `SUM(revenue)` | `category` | Horizontal bars, descending |
| Top Menu Items | `SUM(revenue)` | `menu_item` | Horizontal bars, top 10 filter |
| Revenue by Hour | `hour` | `SUM(revenue)` | Line with circle marks |
| Average Daily Revenue by Weekday | `weekday` | `AVG(Average Daily Revenue)` | Bars sorted Monday through Sunday |

Add a dashboard action so selecting a category filters the menu-item chart. Keep tooltips concise and show revenue, revenue share, units sold, and POS records.

## Dashboard 2: Staffing and Models

![Staffing and model preview](screenshots/tableau-staffing-models.png)

### Staffing heatmap

- Source: `Staffing Schedule`
- Columns: `Hour` as discrete
- Rows: `Weekday`, manually ordered Monday through Sunday
- Marks: Square
- Color and Label: `Staffing Demand Score`
- Format: percentage with no decimals
- Use a sequential blue-green palette and visually distinguish scores at or above `0.50`.

### Staffing recommendations

Create a text table with `Weekday`, `Hour`, and `Full Staffing Recommended`. Filter the table to `True`. Add this note under the view:

> Full staffing is a top-quartile units-sold proxy predicted from schedule-time features. Validate it against real labor schedules, reservations, and service outcomes before operational use.

### Model comparison

- Source: `Model Results`
- Filter: `Model Task`
- Rows: `Model`
- Measure Values: Accuracy, Precision, Recall, F1, ROC-AUC, CV F1 Mean
- Use grouped bars or a highlight table.
- Keep null Precision and Recall values blank for the high-value POS record task because those metrics were not exported by that evaluation pipeline.

## Visual Style

- Use a white or very light gray background.
- Use dark charcoal text and a restrained mix of teal, coral, gold, and blue.
- Keep titles left-aligned and labels direct.
- Avoid dashboard-level decorative containers and unnecessary legends.
- Use currency formatting for revenue and percentages for model scores.

## Refresh the Data

From the repository root, run:

```bash
python scripts/export_tableau_data.py
python scripts/create_tableau_previews.py
```

Then open Tableau and refresh the Excel connection. The workbook snapshot is generated for this repository; the CSV files are the reproducible model outputs used to rebuild it.

## Publish to Tableau Public

1. Sign in to [Tableau Public](https://public.tableau.com/).
2. Select **Create**, then upload `data/restaurant_pos_tableau.xlsx`.
3. Build the two dashboards using the specifications above, or open the workbook in Tableau Desktop/Public Edition and publish from there.
4. Name the visualization `Restaurant POS Sales Analytics`.
5. Confirm that **Allow access** or **Download** settings do not expose anything beyond this public Kaggle-derived dataset.
6. Copy the public visualization URL into the main project README under the title.
7. Replace these design-preview images with screenshots from the published Tableau workbook when it is live.

Tableau Public workbooks and their underlying data are public. This dataset is suitable because it is already public and contains no customer or employee personal information beyond simulated names and IDs.

## CV Description

> Built a Tableau reporting layer for 5,000 restaurant POS records, combining revenue and menu analysis with model evaluation and weekday-hour staffing-demand recommendations.
