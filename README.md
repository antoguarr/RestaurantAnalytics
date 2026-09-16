# Restaurant POS Sales Analytics

[GitHub Repository](https://github.com/antoguarr/RestaurantAnalytics)

![Restaurant POS Analytics dashboard](docs/screenshots/dashboard-live.png)

## Project Overview

This project analyzes simulated point-of-sale records for a steakhouse restaurant. The goal is to identify revenue drivers, understand menu and server performance, uncover sales patterns by day and time, and run a classification experiment identifying characteristics associated with high-value POS records.

The analysis is designed as a business-facing data analytics project, combining exploratory data analysis, SQL, Power BI preparation, interactive dashboarding, machine learning evaluation, and actionable recommendations for restaurant management.

## Dashboard Screenshots

### Menu and Operations

![Menu and operations dashboard](docs/screenshots/dashboard-menu-operations.png)

### Model Evaluation

![Model evaluation dashboard](docs/screenshots/dashboard-model-evaluation.png)

## Business Questions

This project investigates the following questions:

- Which menu categories and items generate the most revenue?
- Which days and hours produce the strongest sales?
- How does server performance compare across revenue and POS record volume?
- Are certain order types or payment methods associated with higher revenue?
- Which recorded characteristics are associated with high-revenue POS records?

## Dataset

The dataset contains 5,000 simulated restaurant POS records from 2024.

Each row represents one menu-item line recorded by the POS system and includes:

- Date and time recorded
- Menu item and category
- Quantity ordered
- Price per item
- Total revenue
- Payment method
- Order type
- Server ID and server name

The source does not include an order or receipt ID. Multiple line items therefore cannot be grouped into complete restaurant checks, so this project reports **POS record count** and **average line revenue** rather than transaction count or average order value.

Dataset file:

```text
Data/steakhouse_pos_simulated_data.csv
```

## Tools Used

- Python
- pandas
- matplotlib
- scikit-learn
- Jupyter Notebook
- Streamlit
- Plotly
- Power BI
- SQL

## Methodology

The project is organized so that reusable logic is separated from the notebook:

- `src/data_cleaning.py` loads the POS data, validates required columns, standardizes data types, and removes duplicate rows.
- `src/feature_engineering.py` creates calendar, hourly, weekend, and high-revenue target features.
- `src/model.py` builds and evaluates the machine learning pipeline.
- `notebooks/eda.ipynb` uses those modules to run the analysis and present business insights.
- `app.py` turns the analysis into an interactive Streamlit dashboard for business exploration.
- `scripts/export_powerbi_data.py` exports a cleaned, feature-enriched dataset for Power BI.
- `scripts/run_sql_analysis.py` runs SQL queries against the prepared dataset and exports result tables.
- `scripts/create_readme_screenshots.py` generates dashboard screenshots for the README.
- `powerbi/` contains Power BI report instructions, suggested DAX measures, and the export-ready CSV.
- `sql/` contains reusable SQL queries and exported SQL result tables.

## Key Findings

### 1. Entrees contribute the largest revenue share

Entrees generated **$272,974.90**, representing approximately **62.0%** of total revenue. This identifies entrees as the largest revenue contributor, but it does not establish profitability because product costs are unavailable.

### 2. Desserts may offer an upselling opportunity

Desserts represented approximately **4.0%** of revenue, or **$17,739.00**. Because desserts are lower-priced than entrees, this does not by itself prove poor performance; it suggests an opportunity to test dessert upselling, bundles, or server prompts.

### 3. Three premium steaks contribute over half of revenue

New York Strip, Filet Mignon, and Ribeye Steak generated a combined **$228,576.70**, accounting for approximately **51.9%** of total revenue. Their contribution reflects both sales volume and higher menu prices, so revenue alone should not be interpreted as margin or item popularity.

### 4. Saturday has the strongest average daily revenue

Saturday produced the highest average daily revenue at approximately **$1,421.85** per day. This was about **25% higher** than Thursday, the weakest day by average daily revenue.

### 5. Dinner hours outperform lunch hours

The strongest revenue hours were **7 PM, 8 PM, and 9 PM**, each generating roughly **$47,000-$49,000** in total revenue. Average line revenue during these peak dinner hours was approximately **$112**, compared with about **$66-$67** during early afternoon hours.

### 6. Server revenue is balanced, with Nina leading

Nina generated the highest total revenue at **$91,506.80**, representing approximately **20.8%** of total revenue. Overall server performance was relatively balanced, with the gap between the highest and lowest revenue-generating servers at about **$7,941.70**.

## Model Evaluation

This is a classification experiment identifying characteristics associated with high-value POS records. The target is whether a record's revenue is above the dataset median; it is not a forecast of customer spend or a prediction made before an item is selected.

Features used included:

- Menu item
- Category
- Payment method
- Order type
- Server name
- Weekday
- Hour
- Month
- Weekend indicator

Models were evaluated using a stratified 80/20 holdout split and five-fold stratified cross-validation. Random Forest performed best on holdout F1, while Logistic Regression produced similar cross-validation results with a simpler model:

| Model | Accuracy | F1 | ROC-AUC | CV F1 |
| --- | ---: | ---: | ---: | ---: |
| Random Forest | 0.792 | 0.786 | 0.889 | 0.775 |
| Logistic Regression | 0.773 | 0.763 | 0.881 | 0.768 |
| Dummy Baseline | 0.501 | 0.000 | 0.500 | 0.000 |

The notebook and dashboard expose this comparison directly, followed by the Random Forest confusion matrix, classification report, and feature importances.

Menu item is known only once a customer is ordering and indirectly carries price information. The model is therefore useful for describing patterns associated with higher-value POS records, not for forecasting customer demand or spend before an order begins.

## SQL Analysis

The project includes a small SQL analysis component using SQLite. Queries are stored in:

```text
sql/restaurant_analysis.sql
```

The SQL analysis answers questions such as:

- Which menu categories generate the most revenue?
- Which menu items are the top revenue drivers?
- Which weekdays and hours perform best?
- Which servers generate the most revenue?
- Which servers have the highest dessert revenue share?

SQL outputs are exported to:

```text
sql/results/
```

## Business Recommendations

- Prioritize premium entree promotion, especially steak items that account for the majority of revenue.
- Test dessert upselling strategies and measure whether they increase dessert attachment and revenue.
- Staff peak dinner hours carefully, especially between 7 PM and 9 PM.
- Use Saturday demand patterns to guide inventory planning and scheduling.
- Study top-performing server POS record patterns to form testable training hypotheses, without assuming revenue differences are caused by server behavior.
- Use the classifier as an analytical experiment for identifying high-value record patterns, not as a forecasting or staff-evaluation tool.

## Project Structure

```text
RestaurantAnalytics/
├── .streamlit/
│   └── config.toml
├── .gitignore
├── app.py
├── Data/
│   └── steakhouse_pos_simulated_data.csv
├── docs/
│   └── screenshots/
│       ├── dashboard-live.png
│       ├── dashboard-menu-operations.png
│       ├── dashboard-model-evaluation.png
│       └── dashboard-overview.png
├── notebooks/
│   └── eda.ipynb
├── powerbi/
│   ├── README.md
│   ├── dax_measures.md
│   └── data/
│       └── restaurant_pos_powerbi.csv
├── scripts/
│   ├── create_readme_screenshots.py
│   ├── export_powerbi_data.py
│   └── run_sql_analysis.py
├── sql/
│   ├── README.md
│   ├── restaurant_analysis.sql
│   └── results/
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   └── model.py
├── README.md
└── requirements.txt
```

## How to Run

Clone the repository and install the required Python packages:

```bash
pip install -r requirements.txt
```

Open the notebook:

```bash
jupyter notebook notebooks/eda.ipynb
```

Run the notebook cells from top to bottom to reproduce the exploratory analysis, visualizations, and machine learning model.

To launch the interactive dashboard:

```bash
streamlit run app.py
```

The dashboard includes KPI cards, filters, category and menu item analysis, weekday and hourly revenue trends, server performance, order type analysis, model comparison, confusion matrix, feature importance, and business recommendations.

To run the SQL analysis:

```bash
python scripts/run_sql_analysis.py
```

To refresh the Power BI-ready CSV:

```bash
python scripts/export_powerbi_data.py
```

Then import this file into Power BI:

```text
powerbi/data/restaurant_pos_powerbi.csv
```

Power BI report setup instructions and DAX measures are available in the `powerbi/` folder.

To regenerate README screenshots:

```bash
python scripts/create_readme_screenshots.py
```

## Deployment

The Streamlit dashboard is ready to deploy from GitHub using `app.py` as the main file and `requirements.txt` for dependencies.

Recommended Streamlit Community Cloud settings:

```text
Repository: antoguarr/RestaurantAnalytics
Branch: main
Main file path: app.py
```

After deployment, add the live dashboard link near the top of this README.

## Suggested GitHub Metadata

Recommended repository description:

```text
Interactive restaurant POS analytics project with Python, SQL, Streamlit, Power BI preparation, and machine learning model evaluation.
```

Recommended topics:

```text
python, pandas, streamlit, plotly, scikit-learn, sql, sqlite, powerbi, data-analysis, dashboard, machine-learning, restaurant-analytics
```

## Limitations

- The dataset is sourced from Kaggle and appears to be simulated or highly curated, so the findings should not be interpreted as conclusions about a real restaurant.
- The data is already clean, so the project focuses more on validation, analysis, dashboarding, and modeling than complex data cleaning.
- The dataset has no order or receipt ID. It cannot support true order counts, check-level average order value, basket composition, or dessert attachment rates; all row-level metrics are labeled as POS records or line-item revenue.
- The high-revenue target is created from the POS record revenue median. This is useful for classification practice, but it is not the same as forecasting future demand, customer spend, or profit.
- Revenue is heavily influenced by menu item and price, so the model may learn pricing/category patterns more than deeper customer behavior.
- The dataset does not include important business context such as food cost, margins, table size, customer history, promotions, reservations, weather, or labor costs.

## Future Improvements

- Add a live Streamlit deployment link after publishing the app.
- Build and save the final Power BI `.pbix` file after importing the prepared dataset.
- Add margin or cost data if available to analyze profitability, not only revenue.

## Summary

This project demonstrates the use of Python, SQL, and business intelligence tools to translate restaurant POS records into business insights. It combines revenue analysis, menu performance evaluation, server comparison, time-based sales trends, interactive dashboards, Power BI reporting preparation, and machine learning model evaluation to support operational decision-making.
