# Tableau Calculated Fields

The prepared source already includes the row-level fields needed for the dashboards. Add these calculated fields in Tableau to keep the workbook readable and reusable.

## Core KPIs

### POS Records

```tableau
COUNT([record_id])
```

### Total Revenue

```tableau
SUM([revenue])
```

### Average Line Revenue

```tableau
AVG([revenue])
```

### Units Sold

```tableau
SUM([quantity])
```

### Revenue per Unit

```tableau
SUM([revenue]) / SUM([quantity])
```

## Comparisons

### Revenue Share

Set **Compute Using** to the dimension displayed in the view.

```tableau
SUM([revenue]) / TOTAL(SUM([revenue]))
```

### Average Daily Revenue

```tableau
{ FIXED [date] : SUM([revenue]) }
```

Use `AVG([Average Daily Revenue])` when comparing weekdays. This avoids rewarding a weekday merely because it appears more often in the calendar.

### High-Value Record Rate

```tableau
AVG(INT([high_revenue]))
```

## Staffing

### Staffing Recommendation

```tableau
IF [Staffing Demand Score] >= 0.5 THEN "Full staffing"
ELSE "Standard staffing"
END
```

### Peak Dinner Window

```tableau
IF [Hour] >= 17 AND [Hour] <= 22 THEN "Dinner peak window"
ELSE "Lunch / early service"
END
```

The staffing recommendation is a model-based demand proxy. It is not an observed labor requirement and should not be presented as a final staffing decision.
