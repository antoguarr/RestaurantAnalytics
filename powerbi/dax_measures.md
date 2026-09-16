# Power BI DAX Measures

Use these measures after importing `powerbi/data/restaurant_pos_powerbi.csv` into Power BI.

These examples assume the imported table is named `POS`. If Power BI gives the table a different name, either rename the table to `POS` or update the table name in each measure.

## Core KPI Measures

```DAX
Total Revenue = SUM('POS'[revenue])
```

```DAX
Total Transactions = COUNTROWS('POS')
```

```DAX
Units Sold = SUM('POS'[quantity])
```

```DAX
Average Order Value = AVERAGE('POS'[revenue])
```

```DAX
Average Unit Price = AVERAGE('POS'[price_per_item])
```

## Revenue Share Measures

```DAX
Revenue Share =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL('POS'))
)
```

```DAX
Category Revenue Share =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL('POS'[category]))
)
```

## High-Revenue Order Measures

```DAX
High Revenue Transactions =
CALCULATE(
    [Total Transactions],
    'POS'[high_revenue] = TRUE()
)
```

```DAX
High Revenue Transaction Rate =
DIVIDE(
    [High Revenue Transactions],
    [Total Transactions]
)
```

## Time-Based Measures

```DAX
Average Daily Revenue =
AVERAGEX(
    VALUES('POS'[date]),
    [Total Revenue]
)
```

```DAX
Weekend Revenue =
CALCULATE(
    [Total Revenue],
    'POS'[is_weekend] = TRUE()
)
```

```DAX
Weekday Revenue =
CALCULATE(
    [Total Revenue],
    'POS'[is_weekend] = FALSE()
)
```

## Suggested Formatting

- Format revenue measures as Currency.
- Format share and rate measures as Percentage.
- Format transaction counts as Whole number.
- Format quantity measures with one decimal place.
