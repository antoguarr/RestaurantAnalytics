# Restaurant POS Sales Analysis

## Project Overview

This project analyzes simulated point-of-sale transaction data for a steakhouse restaurant. The goal is to identify revenue drivers, understand menu and server performance, uncover sales patterns by day and time, and test whether order-level information can be used to predict high-revenue transactions.

The analysis is designed as a business-facing data analytics project, combining exploratory data analysis, visualizations, basic machine learning, and actionable recommendations for restaurant management.

## Business Questions

This project investigates the following questions:

- Which menu categories and items generate the most revenue?
- Which days and hours produce the strongest sales?
- How does server performance compare across revenue and order volume?
- Are certain order types or payment methods associated with higher revenue?
- Can transaction details help predict whether an order will be high revenue?

## Dataset

The dataset contains 5,000 simulated restaurant POS transactions from 2024.

Each row represents one transaction line item and includes:

- Date and time of transaction
- Menu item and category
- Quantity ordered
- Price per item
- Total revenue
- Payment method
- Order type
- Server ID and server name

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

## Methodology

The project is organized so that reusable logic is separated from the notebook:

- `src/data_cleaning.py` loads the POS data, validates required columns, standardizes data types, and removes duplicate rows.
- `src/feature_engineering.py` creates calendar, hourly, weekend, and high-revenue target features.
- `src/model.py` builds and evaluates the machine learning pipeline.
- `notebooks/eda.ipynb` uses those modules to run the analysis and present business insights.
- `app.py` turns the analysis into an interactive Streamlit dashboard for business exploration.

## Key Findings

### 1. Entrees are the main revenue driver

Entrees generated **$272,974.90**, representing approximately **62.0%** of total revenue. This makes entree sales the strongest contributor to overall restaurant performance.

### 2. Desserts are underperforming

Desserts generated only **$17,739.00**, or about **4.0%** of total revenue. This suggests a potential opportunity to increase average order value through dessert upselling, bundled offers, or server prompts.

### 3. The top steak items drive over half of revenue

New York Strip, Filet Mignon, and Ribeye Steak generated a combined **$228,576.70**, accounting for approximately **51.9%** of total revenue. These premium items are the restaurant's core sales drivers.

### 4. Saturday has the strongest average daily revenue

Saturday produced the highest average daily revenue at approximately **$1,421.85** per day. This was about **25% higher** than Thursday, the weakest day by average daily revenue.

### 5. Dinner hours outperform lunch hours

The strongest revenue hours were **7 PM, 8 PM, and 9 PM**, each generating roughly **$47,000-$49,000** in total revenue. Average order value during these peak dinner hours was approximately **$112**, compared with about **$66-$67** during early afternoon hours.

### 6. Server revenue is balanced, with Nina leading

Nina generated the highest total revenue at **$91,506.80**, representing approximately **20.8%** of total revenue. Overall server performance was relatively balanced, with the gap between the highest and lowest revenue-generating servers at about **$7,941.70**.

## Machine Learning Component

A Random Forest classification model was built to predict whether a transaction would be classified as high revenue, where high revenue is defined as revenue above the dataset median.

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

The model achieved approximately **78.7% accuracy** on the test set.

This model should be interpreted as a decision-support experiment rather than a production forecasting system. Since revenue is strongly influenced by item price and quantity, the model is most useful for understanding patterns associated with higher-value orders.

## Business Recommendations

- Prioritize premium entree promotion, especially steak items that account for the majority of revenue.
- Introduce dessert upselling strategies to improve performance in the lowest-revenue category.
- Staff peak dinner hours carefully, especially between 7 PM and 9 PM.
- Use Saturday demand patterns to guide inventory planning and scheduling.
- Study top-performing server behavior to identify successful upselling or service patterns.
- Use predictive modeling as a supporting tool for identifying high-value order patterns, not as the sole basis for staffing or performance decisions.

## Project Structure

```text
RestaurantAnalytics/
├── .gitignore
├── app.py
├── Data/
│   └── steakhouse_pos_simulated_data.csv
├── notebooks/
│   └── eda.ipynb
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

The dashboard includes KPI cards, filters, category and menu item analysis, weekday and hourly revenue trends, server performance, order type analysis, and model feature importance.

## Future Improvements

- Export charts to a `figures/` folder and include them in this README.
- Add more model evaluation metrics such as confusion matrix, ROC-AUC, and cross-validation.
- Compare the Random Forest model against simpler baseline models.

## Summary

This project demonstrates the use of Python-based data analysis to translate restaurant transaction data into business insights. It combines revenue analysis, menu performance evaluation, server comparison, time-based sales trends, and introductory machine learning to support operational decision-making.
