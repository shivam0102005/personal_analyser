# 💰 AI Personal Finance Analyzer

> A complete, industry-level Data Analytics portfolio project for analyzing personal financial transactions — with interactive dashboards, ML predictions, anomaly detection, and automated PDF/Excel reports.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange?logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Plotly-5.14+-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Dashboard Preview

The dashboard features a dark-themed, multi-tab interface with:

- 📊 Interactive pie charts, bar charts, line charts, and heatmaps
- 💡 Automated financial insights
- 🤖 ML-powered spending predictions
- 🚨 Anomaly / suspicious transaction detection
- 💵 Budget tracking with gauge charts
- 📄 One-click PDF & Excel report export

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Multi-format Upload** | CSV, Excel (.xlsx), PDF bank statements, TXT files |
| **Auto Categorization** | Rule-based keyword matching (Food, Transport, Shopping, etc.) |
| **Interactive Dashboard** | Streamlit with dynamic filters (Month, Year, Category, Type) |
| **6 Chart Types** | Pie, Bar, Line, Stacked Bar, Heatmap, Scatter |
| **Automated Insights** | 9+ natural-language insights generated automatically |
| **Budget Tracking** | Set per-category budgets with gauge-chart visualizations |
| **ML Predictions** | Linear Regression + Random Forest for next-month forecast |
| **Spending Clustering** | K-Means to identify spending profile patterns |
| **Anomaly Detection** | Z-Score + Isolation Forest for unusual transactions |
| **Report Export** | Multi-page PDF report + multi-sheet Excel workbook |

---

## 📁 Project Structure

```
personal-finance-analyzer/
│
├── data/
│   ├── sample_transactions.csv    ← Sample dataset (3 months, 90 transactions)
│   ├── uploads/                   ← User-uploaded files
│   └── processed_data/            ← Cleaned output files
│
├── src/
│   ├── data_processing/
│   │   ├── data_cleaning.py       ← Full cleaning pipeline (DataCleaner class)
│   │   └── file_converter.py      ← CSV / Excel / PDF / TXT → DataFrame
│   │
│   ├── analytics/
│   │   ├── expense_analysis.py    ← Pandas groupby analytics engine
│   │   └── insight_generator.py  ← Automated insight text generation
│   │
│   ├── ml_models/
│   │   ├── prediction_model.py    ← LR + Random Forest spending forecast
│   │   ├── clustering_model.py    ← K-Means spending pattern clustering
│   │   └── anomaly_detection.py  ← Z-Score + Isolation Forest anomalies
│   │
│   ├── visualization/
│   │   └── charts.py              ← All Plotly + Matplotlib/Seaborn charts
│   │
│   ├── dashboard/
│   │   └── streamlit_app.py       ← Main Streamlit dashboard (7 tabs)
│   │
│   └── reports/
│       └── report_generator.py   ← PDF + Excel report generation
│
├── notebooks/                     ← Jupyter notebooks for EDA
├── reports/                       ← Generated reports saved here
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/personal-finance-analyzer.git
cd personal-finance-analyzer
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

```bash
streamlit run src/dashboard/streamlit_app.py
```

The app will open at **http://localhost:8501** in your browser.

---

## 📊 Usage

### Option A — Use Sample Data
Click **"📋 Use Sample Data"** in the sidebar. The app loads 3 months of realistic Indian transaction data.

### Option B — Upload Your Own File

| Format | Notes |
|---|---|
| **CSV** | Must have columns: Date, Description, Amount (others auto-detected) |
| **Excel** | `.xlsx` or `.xls`; same column requirements |
| **PDF** | Bank statements with table-formatted or text transactions |
| **TXT** | Pipe/comma/tab delimited or free-form text statements |

---

## 🧠 Standard Data Schema

All uploaded data is normalized to:

| Column | Type | Description |
|---|---|---|
| `Date` | datetime | Transaction date |
| `Description` | str | Raw transaction description |
| `Category` | str | Auto-detected category |
| `Amount` | float | Absolute transaction amount (₹) |
| `Transaction_Type` | str | `Debit` or `Credit` |
| `Merchant` | str | Extracted merchant name |
| `Payment_Method` | str | UPI / Credit Card / Debit Card / etc. |

---

## 🤖 Machine Learning Details

### Spending Prediction (`prediction_model.py`)
- **Features**: month index, month number, 3-month rolling average, lag-1, lag-2
- **Models**: `LinearRegression` and `RandomForestRegressor` (100 trees)
- **Output**: ensemble prediction = average of both models
- **Requirement**: ≥ 3 months of transaction data

### Spending Clustering (`clustering_model.py`)
- **Algorithm**: K-Means (k=2–5, configurable via UI slider)
- **Feature matrix**: monthly category-level spending pivot table
- **Visualization**: PCA-reduced 2D scatter plot with cluster labels
- **Labels**: Food-Heavy Spender, Shopping Enthusiast, Balanced Spender, etc.

### Anomaly Detection (`anomaly_detection.py`)
- **Z-Score**: flags transactions >2.5σ above per-category mean
- **Isolation Forest**: `contamination=0.05`, features: Amount + Category + Day-of-Week
- Both results are combined and deduplicated before display

---

## 📈 Analytics Engine

All analytics use `pandas.groupby()` operations in `expense_analysis.py`:

```python
# Example: Category spending with percentage
category_spending(df)

# Example: Monthly trends with MoM change
monthly_spending(df)

# Example: Budget vs actual for a given month
budget_vs_actual(df, budgets, year=2025, month=1)
```

---

## 🗂️ Expense Categories

The rule-based categorizer (`data_cleaning.py`) maps keywords to categories:

| Category | Sample Keywords |
|---|---|
| Food | swiggy, zomato, restaurant, pizza, kfc |
| Transport | uber, ola, petrol, metro, rapido |
| Shopping | amazon, flipkart, myntra, ajio |
| Entertainment | netflix, spotify, bookmyshow, pvr |
| Utilities | electricity, water, jio, airtel, bill |
| Groceries | dmart, bigbasket, zepto, blinkit |
| Healthcare | pharmacy, apollo, doctor, hospital |
| Health & Fitness | gym, cult.fit, yoga |
| Income | salary, credit, bonus, refund |

You can **manually edit categories** in the "Categories" tab of the dashboard.

---

## 📄 Report Generation

### PDF Report (3 pages)
1. Title page with KPI cards and insights preview
2. Category pie chart + monthly bar chart
3. Category/merchant tables + full insights list

### Excel Report (5 sheets)
- `Transactions` — cleaned raw data
- `Summary` — key metrics
- `Category_Breakdown` — spending by category
- `Monthly_Trends` — month-over-month data
- `Top_Merchants` — top 10 merchants
- `Budget_Tracking` — budget vs actual (if budgets set)

---

## 🛠️ Technology Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Pandas + NumPy | Data processing & analytics |
| Streamlit | Interactive web dashboard |
| Plotly | Interactive charts |
| Matplotlib + Seaborn | Static charts (PDF reports) |
| Scikit-learn | ML models (LR, RF, KMeans, IsoForest) |
| pdfplumber | PDF bank statement parsing |
| openpyxl | Excel read/write |
| Matplotlib PdfPages | PDF report generation |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

---

## 📝 License

MIT License — free to use for personal and commercial projects.

---

## 👤 Author

Built as a **portfolio project** for Data Analyst / Data Scientist roles.

⭐ If this helped you, give it a star on GitHub!
