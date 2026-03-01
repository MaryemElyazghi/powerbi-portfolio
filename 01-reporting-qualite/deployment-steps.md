# Power BI Service — Deployment Guide

Step-by-step deployment of the Quality Incidents report to Power BI Service,
including workspace setup, RLS configuration and scheduled refresh.

---

## Prerequisites

- Power BI Desktop (latest version)
- Microsoft account with Power BI access (free tier sufficient)
- Report file: `rapport_qualite.pbix`

---

## Step 1 — Publish to Power BI Service

1. Open `rapport_qualite.pbix` in Power BI Desktop
2. Click **Home → Publish**
3. Sign in with your Microsoft account
4. Select destination: **My workspace**
5. Wait for upload confirmation
6. Click the link to open the report in the browser

**Verification:** Navigate to `app.powerbi.com` → My workspace → confirm report is visible.

---

## Step 2 — Row-Level Security (RLS)

### Define roles in Power BI Desktop

Go to **Modeling → Manage Roles → Create**

| Role Name | Table | DAX Filter |
|-----------|-------|------------|
| `Casablanca` | incidents_qualite | `[Region] = "Casablanca"` |
| `Rabat` | incidents_qualite | `[Region] = "Rabat"` |
| `Tanger` | incidents_qualite | `[Region] = "Tanger"` |
| `Marrakech` | incidents_qualite | `[Region] = "Marrakech"` |
| `Agadir` | incidents_qualite | `[Region] = "Agadir"` |

Save roles → re-publish the report.

### Assign users to roles in Power BI Service

1. Go to `app.powerbi.com` → Datasets → `rapport_qualite`
2. Click **⋮ → Security**
3. Select role (e.g. `Casablanca`) → add user email → click **Add**
4. Repeat for each region role

**Test RLS:**
In Power BI Service → dataset menu → **Test as role** → select `Casablanca`
→ verify only Casablanca data is visible.

---

## Step 3 — Scheduled Refresh

1. Go to `app.powerbi.com` → Datasets → `rapport_qualite`
2. Click **⋮ → Settings**
3. Expand **Scheduled refresh**
4. Toggle **Keep your data up to date → ON**
5. Set frequency: **Daily**
6. Set time: **08:00**
7. Click **Apply**

**Note:** Refresh requires a gateway for on-premises data sources.
For local CSV files, upload the dataset directly to Power BI Service.

---

## Step 4 — Share the Report

1. Open the report in Power BI Service
2. Click **Share** (top right)
3. Enter recipient email addresses
4. Set permissions: **Can view** (read-only) or **Can edit**
5. Check **Send email notification**
6. Click **Send**

---

## CI/CD — PBIX Version Control

The report file is tracked in Git. Deployment process:

```
Local development → Push to GitHub → CI validates data quality → Manual publish to PBI Service
```

For automated deployment, Power BI REST API or `pbicli` can be used:

```bash
# Install Power BI CLI
npm install -g @powerbi-tools/pbicli

# Deploy (requires service principal credentials)
pbicli report import --workspace "My Workspace" --file rapport_qualite.pbix
```

---

## Architecture

```
Raw Data (CSV/API)
       ↓
Python ETL (Pandas + VBA)
       ↓
PostgreSQL / Local CSV
       ↓
Power BI Desktop (DAX modeling)
       ↓
Power BI Service (workspace + RLS + refresh)
       ↓
End Users (filtered by region role)
```