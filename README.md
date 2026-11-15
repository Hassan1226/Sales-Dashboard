# 📊 Sales Report Dashboard

An interactive dashboard built with **Streamlit** and **Plotly** that visualizes customer and product performance. It is built on two SQL Server reporting views (`gold.report_customer` and `gold.report_product`) and runs on exported CSV files or on built-in sample data.

The theme is black with orange, mauve and blue accents. Charts show their values directly on the bars and donuts.

<img width="558" height="571" alt="image" src="https://github.com/user-attachments/assets/1e498593-045e-4f52-bb4f-df3c3cc2aef8" />


## Features

- **Two dashboards** in one app: **Customers** and **Products**
- **KPI cards** for total sales, orders, quantity and average values
- **Interactive charts** (Plotly) with value labels, hover details and donut percentages
- **Month filter:** a 4 × 3 grid of buttons (Jan to Dec); select one or several months
- **Dropdown filters:** customer segment and age group, or product category and product segment
- **Data tables** with CSV download of the filtered rows
- **Two data sources:** built-in sample data, or your own CSV exports

### Customers tab

| Section | Content |
|---|---|
| KPIs | Sum of Sales, Customers, Sum of Orders, Avg Order Value |
| Charts | Top Customers, Customers by Segment, Sales by Age Group, Avg Monthly Spend, Orders by Age Group, Sales by Lifespan |

### Products tab

| Section | Content |
|---|---|
| KPIs | Sum of Sales, Sum of Quantity, Sum of Orders, Avg Selling Price |
| Charts | Top Products, Sales by Category, Sales by Sub-Category, Avg Monthly Revenue, Quantity by Segment, Top Sub-Categories by Units |

## Project structure

```
.
├── app.py                  # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Dark theme settings
├── sql/
│   ├── customer_report.sql # Creates gold.report_customer
│   └── product_report.sql  # Creates gold.report_product
└── README.md
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <https://github.com/Hassan1226/Sales-Dashboard.git>
```

### 2. Install dependencies

Python 3.9 or newer is recommended.

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

## Using your own data

1. Create the views in SQL Server by running the scripts in the `sql/` folder.
2. Export each view to CSV, for example from SSMS: run `SELECT * FROM gold.report_customer` and save the results as CSV.
3. In the app sidebar, choose **CSV files** as the data source.
4. Upload `report_customer.csv` and/or `report_product.csv`. Any file you skip falls back to sample data.

### Expected columns

**Customer CSV** (`gold.report_customer`):
`customer_key`, `customer_number`, `customer_name`, `age`, `age_group`, `customer_segment`, `last_order_date`, `recency`, `total_orders`, `total_sales`, `total_quantity`, `total_products`, `lifespan`, `avg_order_value`, `avg_monthly_spend`

**Product CSV** (`gold.report_product`):
`product_key`, `product_name`, `category`, `subcategory`, `cost`, `last_sale_date`, `recency_in_months`, `product_segment`, `lifespan`, `total_orders`, `total_sales`, `total_quantity`, `total_customers`, `avg_selling_price`, `avg_order_revenue`, `avg_monthly_revenue`

## Segmentation rules

These rules come from the SQL views.

| Segment | Rule |
|---|---|
| **VIP Customers** | Lifespan of 12 months or more and total sales above 5,000 |
| **Regular Customers** | Lifespan of 12 months or more and total sales of 5,000 or less |
| **New Customers** | Lifespan under 12 months |
| **High-Performer** (product) | Total sales above 50,000 |
| **Mid-Range** (product) | Total sales from 10,000 to 50,000 |
| **Low-Performer** (product) | Total sales below 10,000 |

Age groups: Under Age (below 20), 20-29, 30-39, 40-49 and 50 and Above.

## Notes and limitations

- The **month filter** uses `last_order_date` (customers) and `last_sale_date` (products). It ignores the year, and because the views are summarized per customer and per product, it filters those summaries rather than individual orders.
- For a true monthly sales trend, the app would need order-level data from `gold.fact_sales`.
- `recency` in the SQL views is calculated with `GETDATE()`, so it reflects the day the view was queried, not the day you export it.

## Customizing the theme

- **Chart colors:** edit the `PAL` list near the top of the theme section in `app.py`.
- **Page styling** (background, cards, banner): edit the CSS block in `app.py`.
- **Streamlit widget colors:** edit `.streamlit/config.toml`.

## Tech stack

- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)

