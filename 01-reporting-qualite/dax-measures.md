# DAX Measures — Quality Incidents Dashboard

All measures used in the Power BI report with formulas, purpose and formatting notes.

---

## 📐 Table: Calendrier (Date Table)

Created via **Modeling → New Table**:

```dax
Calendrier =
ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2025,12,31)),
    "Annee",       YEAR([Date]),
    "Mois_Num",    MONTH([Date]),
    "Mois_Nom",    FORMAT([Date], "MMMM"),
    "Trimestre",   "T" & QUARTER([Date]),
    "Semaine",     WEEKNUM([Date]),
    "Jour_Semaine",FORMAT([Date], "dddd"),
    "Annee_Mois",  FORMAT([Date], "YYYY-MM"),
    "Annee_Mois_Num", YEAR([Date]) * 100 + MONTH([Date])
)
```

> Relationship: `Calendrier[Date]` → `incidents_qualite[Date_Incident]`
> Cardinality: One-to-Many (1:*) | Filter direction: Single (Calendrier → incidents)

---

## 📊 Core KPI Measures

### 1. Incidents Ce Mois
```dax
Incidents Ce Mois =
COUNTROWS('incidents_qualite')
```
> Counts all rows in current filter context. Used as base measure for all other calculations.
> Format: Whole number

---

### 2. Taux Resolution
```dax
Taux Resolution =
DIVIDE(
    CALCULATE(
        COUNTROWS('incidents_qualite'),
        'incidents_qualite'[Resolu] = 1
    ),
    COUNTROWS('incidents_qualite'),
    0
)
```
> % of resolved incidents over total. Main quality KPI.
> Format: Percentage, 1 decimal place

---

### 3. Delai Moyen Resolution
```dax
Delai Moyen Resolution =
AVERAGEX(
    FILTER(
        'incidents_qualite',
        'incidents_qualite'[Resolu] = 1
    ),
    'incidents_qualite'[Delai_Resolution_Jours]
)
```
> Average resolution time in days — only on resolved incidents (excludes blanks).
> Format: Whole number

---

### 4. Cout Total Incidents
```dax
Cout Total Incidents =
SUM('incidents_qualite'[Cout_Incident])
```
> Total financial impact of all incidents in filter context.
> Format: Currency, 0 decimal places

---

### 5. Cout Incidents Critiques
```dax
Cout Incidents Critiques =
CALCULATE(
    [Cout Total Incidents],
    'incidents_qualite'[Severite] = "Critique"
)
```
> Financial impact of critical-severity incidents only.
> Format: Currency, 0 decimal places

---

### 6. Score Satisfaction
```dax
Score Satisfaction =
ROUND(
    AVERAGE('incidents_qualite'[Satisfaction_Score]),
    2
)
```
> Average satisfaction score (1–5 scale) post-incident.
> Format: Decimal number, 1 decimal place

---

## 📅 Time Intelligence Measures

### 7. Incidents Mois Precedent
```dax
Incidents Mois Precedent =
CALCULATE(
    [Incidents Ce Mois],
    PREVIOUSMONTH(Calendrier[Date])
)
```
> Incident count for the previous month. Requires active date relationship.
> Format: Whole number

---

### 8. Variation MoM (Month-over-Month)
```dax
Variation MoM =
VAR current = [Incidents Ce Mois]
VAR previous = [Incidents Mois Precedent]
RETURN
    DIVIDE(current - previous, previous, 0)
```
> % change vs previous month. Negative = improvement (fewer incidents).
> Format: Percentage, 1 decimal place
> Note: requires date slicer on the page to provide filter context.

---

### 9. Variation Dernier Mois (auto — no slicer needed)
```dax
Variation Dernier Mois =
VAR last =
    MAXX(ALL('incidents_qualite'), 'incidents_qualite'[Date_Incident])
VAR m  = MONTH(last)
VAR y  = YEAR(last)
VAR pm = IF(m = 1, 12, m - 1)
VAR py = IF(m = 1, y - 1, y)
VAR current =
    CALCULATE(
        COUNTROWS('incidents_qualite'),
        MONTH('incidents_qualite'[Date_Incident]) = m,
        YEAR('incidents_qualite'[Date_Incident])  = y
    )
VAR previous =
    CALCULATE(
        COUNTROWS('incidents_qualite'),
        MONTH('incidents_qualite'[Date_Incident]) = pm,
        YEAR('incidents_qualite'[Date_Incident])  = py
    )
RETURN
    DIVIDE(current - previous, previous, 0)
```
> Self-contained MoM — always shows latest month vs month before. No slicer required.
> Format: Percentage, 1 decimal place

---

## 🏆 Ranking Measures

### 10. Rang Technicien
```dax
Rang Technicien =
RANKX(
    ALL('incidents_qualite'[Technicien]),
    [Taux Resolution],
    ,
    DESC,
    DENSE
)
```
> Ranks technicians by resolution rate. Rank 1 = best performer.
> Format: Whole number

---

### 11. Taux Resolution 7 Jours Glissants
```dax
Taux Resolution 7j =
CALCULATE(
    [Taux Resolution],
    DATESINPERIOD(
        Calendrier[Date],
        LASTDATE(Calendrier[Date]),
        -7,
        DAY
    )
)
```
> Rolling 7-day resolution rate — useful for detecting short-term quality drops.
> Format: Percentage, 1 decimal place

---

## 🔗 DAX Patterns Used

| Pattern | Measures |
|---------|----------|
| `CALCULATE` + filter | Taux Resolution, Cout Critiques |
| `DIVIDE` (safe division) | Taux Resolution, Variation MoM |
| `AVERAGEX` + FILTER | Delai Moyen Resolution |
| `PREVIOUSMONTH` | Incidents Mois Precedent |
| `DATESINPERIOD` | Taux Resolution 7j |
| `RANKX` + `ALL` | Rang Technicien |
| `VAR / RETURN` | Variation MoM, Variation Dernier Mois |
| `MAXX` + `ALL` | Variation Dernier Mois (auto) |