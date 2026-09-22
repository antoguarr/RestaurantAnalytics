# Restaurant POS Sales Analytics

[GitHub Repository](https://github.com/antoguarr/RestaurantAnalytics)

**Project status: Complete** | The repository includes Python analysis, SQL, machine learning, a Streamlit dashboard, a staffing-demand model, a Tableau reporting layer, and a Power BI-ready data layer.

![Restaurant POS Analytics dashboard](docs/screenshots/dashboard-live.png)

## Project Overview

This project analyzes 5,000 simulated point-of-sale records from a steakhouse restaurant. It follows an end-to-end analytics workflow: define business questions, extract and validate the source data, explore performance, reproduce key analysis in SQL, engineer features, evaluate machine learning models, and communicate the results through business intelligence dashboards.

The project is designed as a portfolio case study in business-facing analytics. Its purpose is to show how technical analysis can be translated into measured findings, operational recommendations, and reusable reporting assets.

```mermaid
flowchart LR
    A["Business questions"] --> B["CSV extraction"]
    B --> C["Cleaning and validation"]
    C --> D["Exploratory analysis"]
    D --> E["SQL analysis"]
    E --> F["Feature engineering"]
    F --> G["Model evaluation"]
    G --> H["Dashboards and recommendations"]
```

## Business Questions

The analysis addresses six questions:

1. Which menu categories and items contribute the most revenue?
2. Which weekdays and hours show the strongest sales patterns?
3. How does performance vary across servers, order types, and payment methods?
4. Which recorded characteristics are associated with high-value POS records?
5. When does historical demand suggest that full staffing may be warranted?
6. How can the findings be presented in a format useful to restaurant managers?

## 1. Data Source and Extraction

The source is a Kaggle restaurant POS dataset stored as:

```text
Data/steakhouse_pos_simulated_data.csv
```

This project uses local CSV ingestion rather than an API or production database extract. The raw file remains unchanged, and `src/data_cleaning.py` loads it into pandas for validation and preparation.

| Source characteristic | Value |
| --- | ---: |
| Raw rows | 5,000 |
| Raw columns | 11 |
| Date range | January 1 to December 31, 2024 |
| Menu categories | 5 |
| Menu items | 12 |
| Servers | 5 |

Each row represents one menu-item line recorded by the POS system. The source has no order or receipt ID, so multiple line items cannot be grouped into complete checks. This project therefore reports **POS records** and **average line revenue**, not transaction count or average order value.

## 2. Data Cleaning and Validation

The reusable cleaning pipeline is implemented in `src/data_cleaning.py`.

It performs the following checks and transformations:

1. Validates that every required source column is present.
2. Parses `Date` as a date and `Time` as a time value.
3. Converts quantity, price, and revenue to numeric types.
4. Trims whitespace from categorical fields.
5. Removes exact duplicate rows.
6. Produces a data-quality summary containing missing counts, unique counts, and inferred data types.

The dataset was already highly curated, so the cleaning stage focuses on validation and reproducibility rather than manufacturing unnecessary transformations.

| Quality check | Result |
| --- | ---: |
| Rows before cleaning | 5,000 |
| Rows after cleaning | 5,000 |
| Missing values | 0 |
| Exact duplicate rows | 0 |

## 3. Exploratory Data Analysis

The exploratory workflow is documented in `notebooks/eda.ipynb`. It imports the reusable cleaning and modeling modules instead of placing the full project logic inside the notebook.

The EDA covers:

- Overall revenue, POS record volume, units sold, and average line revenue
- Revenue and units sold by menu category and menu item
- Average daily revenue by weekday
- Revenue and average line revenue by hour
- Server revenue and POS record volume
- Order type and payment method comparisons
- Distribution of the high-value POS record target

The main aggregate measures are:

| Metric | Result |
| --- | ---: |
| Total revenue | $440,324.20 |
| POS records | 5,000 |
| Units sold | 24,067.6 |
| Average line revenue | $88.06 |

## 4. SQL Analysis

The main business aggregations are reproduced in SQLite to demonstrate that the analysis is not limited to pandas.

Queries in `sql/restaurant_analysis.sql` calculate:

- Revenue by category
- Top menu items by revenue
- Average daily revenue by weekday
- Revenue by hour
- Server performance
- Dessert revenue share by server

Run the SQL pipeline with:

```bash
python scripts/run_sql_analysis.py
```

The exported query results are stored in `sql/results/`, and implementation notes are available in `sql/README.md`.

## 5. Feature Engineering

`src/feature_engineering.py` creates reusable analytical and modeling features:

- Hour
- Weekday
- Month number and month name
- Day-of-week index
- Weekend indicator
- High-revenue target based on whether line revenue exceeds the dataset median

`src/staffing_model.py` adds a separate hourly workload dataset. It aggregates POS records into date-hour slots, fills open hours with no recorded sales, and creates cyclical month features for schedule-time prediction.

These two targets answer different questions:

| Target | Interpretation |
| --- | --- |
| High Revenue | Whether an individual POS record is above median line revenue |
| Full Staffing Proxy | Whether an open hour reaches the training period's top quartile of units sold |

Neither target should be interpreted as observed customer spend, profit, or a measured labor requirement.

## 6. Predictive Modeling

### High-Value POS Record Classification

This experiment identifies characteristics associated with above-median line revenue. It is not a forecast made before a customer selects an item.

Features include menu item, category, payment method, order type, server, weekday, hour, month, and weekend status. A stratified 80/20 holdout split and five-fold stratified cross-validation are used to compare three models.

| Model | Accuracy | F1 | ROC-AUC | CV F1 |
| --- | ---: | ---: | ---: | ---: |
| Random Forest | 0.792 | 0.786 | 0.889 | 0.775 |
| Logistic Regression | 0.773 | 0.763 | 0.881 | 0.768 |
| Dummy Baseline | 0.501 | 0.000 | 0.500 | 0.000 |

Random Forest produced the strongest holdout F1. Logistic Regression remained competitive and provides a simpler benchmark. The model is descriptive because menu item is known only during ordering and encodes substantial price information.

![High-value POS record model evaluation](docs/screenshots/dashboard-model-evaluation.png)

### Staffing-Demand Classification

The staffing experiment uses only information available when a schedule is created: hour, weekday, and cyclical month features. The full-staffing proxy is an hour with at least **9 units sold**, the 75th percentile calculated from the training period.

The pipeline creates 4,392 date-hour slots, trains on the first 80% of dates, evaluates on the final 20% beginning October 19, 2024, and applies five-fold time-series cross-validation to the training period.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | CV F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.620 | 0.376 | 0.736 | 0.498 | 0.659 | 0.416 |
| Random Forest | 0.608 | 0.369 | 0.749 | 0.494 | 0.668 | 0.472 |
| Dummy Baseline | 0.744 | 0.000 | 0.000 | 0.000 | 0.500 | 0.000 |

The Dummy model achieves high accuracy by predicting only the majority class and missing every high-workload hour. Random Forest is used for the schedule because it has the strongest time-series CV F1 and identifies **74.9%** of high-workload hours. Its **36.9% precision** also means it produces many conservative full-staffing recommendations.

The resulting schedule flags **5 PM through 10 PM** every day and an additional **Saturday 1 PM** period.

![Staffing-demand model evaluation](docs/screenshots/staffing-model-evaluation.png)

Reproducible model tables are stored in `docs/model_outputs/`.

## 7. Dashboard and BI Delivery

### Streamlit

`app.py` provides an interactive dashboard with filters and six analytical views:

- Executive overview
- Menu analysis
- Operations analysis
- High-value record model evaluation
- Staffing-demand analysis
- Business recommendations

Run it locally with:

```bash
streamlit run app.py
```

### Tableau

The Tableau reporting layer is complete and ready to import.

![Tableau executive overview](tableau/screenshots/tableau-executive-overview.png)

It includes:

- [Tableau-ready Excel workbook](tableau/data/restaurant_pos_tableau.xlsx)
- [Dashboard build and deployment guide](tableau/README.md)
- [Calculated fields](tableau/calculated_fields.md)
- POS record, staffing schedule, model result, and data dictionary sheets
- Executive Overview and Staffing and Models dashboard designs

Publishing to Tableau Public is optional and requires the repository owner's Tableau account. The local Tableau deliverable is complete and version-controlled.

### Power BI

The Power BI layer includes a cleaned export, DAX measures, and a report specification:

- `powerbi/data/restaurant_pos_powerbi.csv`
- `powerbi/dax_measures.md`
- `powerbi/README.md`

The data layer is complete. A final `.pbix` file must be created in Power BI Desktop because that proprietary report format cannot be generated by the Python pipeline.

## 8. Key Findings

1. **Entrees are the largest revenue contributor.** They generated **$272,974.90**, or approximately **62.0%** of total revenue. This does not establish profitability because cost data is unavailable.
2. **Desserts may offer an upselling opportunity.** They represented **$17,739.00**, or approximately **4.0%** of revenue. Their lower share does not by itself prove poor performance because desserts are lower-priced products.
3. **Three premium steaks generated over half of revenue.** New York Strip, Filet Mignon, and Ribeye Steak contributed **$228,576.70**, or approximately **51.9%** of revenue. This reflects both price and volume.
4. **Saturday had the strongest average daily revenue.** Its average of approximately **$1,421.85** was about **25% higher** than Thursday, the weakest weekday on this measure.
5. **Dinner hours outperformed lunch hours.** The strongest hours were **7 PM, 8 PM, and 9 PM**, each generating roughly **$47,000-$49,000** in annual revenue.
6. **Server revenue was relatively balanced.** Nina led with **$91,506.80**, approximately **20.8%** of revenue, while the gap between the highest and lowest server totals was about **$7,941.70**.

## 9. Business Recommendations

- Protect inventory availability for premium entrees and test beverage or side pairings with the leading steak items.
- Test dessert prompts or bundles and measure their effect rather than treating low dessert revenue as proof of poor performance.
- Use Saturday patterns to inform preparation and inventory planning.
- Treat 5 PM through 10 PM as the primary full-staffing window, then adjust using reservations, events, weather, employee availability, and manager knowledge.
- Study top-server POS record patterns as hypotheses for coaching, without assuming that server behavior caused the revenue differences.
- Use the high-value classifier as an analytical experiment, not as a customer-spend forecast or staff-evaluation tool.

## 10. Limitations

- The Kaggle dataset appears simulated or highly curated, so the findings should not be treated as evidence about a real restaurant.
- The source has no order or receipt ID. It cannot support true order counts, check-level average order value, basket composition, or dessert attachment rates.
- Revenue does not measure margin. Food cost, labor cost, discounts, and waste are unavailable.
- The high-revenue target is derived from the dataset median and is strongly influenced by menu item and price.
- The staffing target is a units-sold proxy, not an observed full-staffing requirement.
- The staffing model does not include actual schedules, reservations, events, weather, wait times, employee availability, wage rates, or service targets.
- The hourly grid assumes the restaurant was open every day from 11 AM through 10 PM because no closure calendar is available.

## Project Structure

```text
RestaurantAnalytics/
|-- Data/                         # Original Kaggle CSV
|-- notebooks/eda.ipynb           # Exploratory analysis
|-- src/                           # Cleaning, features, and model pipelines
|-- tests/                         # Staffing pipeline tests
|-- sql/                           # SQLite queries and exported results
|-- powerbi/                       # Power BI source and report guide
|-- tableau/                       # Tableau workbook, sources, and guide
|-- docs/                          # Screenshots and model outputs
|-- scripts/                       # Reproducible export and reporting scripts
|-- app.py                         # Streamlit dashboard
|-- DEPLOYMENT.md                  # Publishing instructions
|-- requirements.txt               # Python dependencies
`-- README.md
```

## Reproduce the Project

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run the Analysis

```bash
jupyter notebook notebooks/eda.ipynb
```

Run the notebook cells from top to bottom.

### 3. Regenerate Analytical Outputs

```bash
python scripts/run_sql_analysis.py
python scripts/run_staffing_model.py
python scripts/export_powerbi_data.py
python scripts/export_tableau_data.py
python scripts/create_tableau_previews.py
python scripts/create_readme_screenshots.py
```

### 4. Run Tests

```bash
python -m unittest discover -s tests -v
```

### 5. Launch Streamlit

```bash
streamlit run app.py
```

## Deployment

Detailed Streamlit and Tableau publishing instructions are available in `DEPLOYMENT.md`.

Recommended Streamlit Community Cloud settings:

```text
Repository: antoguarr/RestaurantAnalytics
Branch: main
Main file path: app.py
```

For Tableau Public, upload `tableau/data/restaurant_pos_tableau.xlsx` and follow `tableau/README.md`. Tableau Public makes the workbook and underlying data public.

## Technology Stack

- Python, pandas, and Jupyter Notebook
- matplotlib and Plotly
- scikit-learn
- SQLite and SQL
- Streamlit
- Tableau
- Power BI

## Next Steps

### Statistical Validation

- Report cross-validation results as mean plus or minus standard deviation so model stability is visible across folds.
- Add 95% bootstrap confidence intervals for precision, recall, F1, ROC-AUC, and the most important business comparisons.
- Add precision-recall AUC, particularly for the imbalanced staffing task.
- Compare staffing thresholds such as `0.40`, `0.50`, and `0.60`, showing precision, recall, F1, and the number of hours flagged at each threshold.
- Evaluate probability calibration with a calibration curve and Brier score before interpreting the staffing-demand score as a real probability.
- Report sample sizes, percentage differences, confidence intervals, and suitable effect sizes for weekday, service-period, category, and server comparisons.

### Expanded Exploratory Analysis

- Expand the EDA with revenue and quantity distributions, outlier checks, monthly trends, daily variability, price-versus-volume analysis, and category and item mix over time.
- Compare lunch and dinner periods using both totals and normalized daily measures.
- Examine whether apparent server and weekday differences remain after accounting for menu mix, hour, and POS record volume.
- Add clearer visual explanations of class balance, probability distributions, model errors, and the records associated with false positives and false negatives.

### Real-World Restaurant Validation

- Repeat the analysis on anonymized real restaurant POS data containing order or receipt IDs so order counts, check-level average order value, basket composition, and dessert attachment can be measured correctly.
- Add actual labor schedules, employee counts, covers, reservations, events, weather, wait times, service outcomes, wages, food costs, discounts, and waste.
- Replace the units-sold staffing proxy with an observed operational target, such as whether scheduled staffing met a defined service-level or labor-efficiency standard.
- Retrain and test the models using chronological holdouts across multiple locations or years to measure performance under real operating conditions.
- Quantify the financial tradeoff between additional labor cost and the cost of understaffing, then choose the staffing threshold using expected business cost.
- Validate recommendations through controlled operational trials, such as dessert-upselling tests or adjusted staffing windows, before making causal claims about real-world outcomes.

### Reporting and Deployment

- Add live Streamlit and Tableau Public links after publishing.
- Build the final Power BI `.pbix` report in Power BI Desktop.
