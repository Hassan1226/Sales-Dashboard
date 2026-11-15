"""Sales report dashboard (Streamlit)

Visualizes the customer and product reports from uploaded CSV files
or from generated sample data.

Run:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Sales report dashboard", page_icon="📊", layout="wide")

# ---------------------------------------------------------------- data loading

def age_group(a):
    return ("Under Age" if a < 20 else "20-29" if a < 30 else "30-39" if a < 40
            else "40-49" if a < 50 else "50 and Above")


@st.cache_data
def sample_data():
    """Generated data with the same columns and segment rules as the SQL views."""
    rng = np.random.default_rng(7)

    n = 320
    lifespan = np.where(rng.random(n) < 0.35, rng.integers(0, 12, n), rng.integers(12, 61, n))
    orders = np.maximum(1, rng.integers(1, 4, n) + lifespan // 3 * rng.integers(0, 2, n))
    sales = (orders * (40 + rng.random(n) * rng.random(n) * 900)).round()
    age = rng.integers(17, 75, n)
    cust = pd.DataFrame({
        "customer_key": np.arange(1, n + 1),
        "customer_number": [f"AW{11000 + i}" for i in range(n)],
        "customer_name": [f"Customer {i + 1}" for i in range(n)],
        "age": age,
        "age_group": [age_group(a) for a in age],
        "customer_segment": np.where((lifespan >= 12) & (sales > 5000), "VIP Customers",
                             np.where(lifespan >= 12, "Regular Customers", "New Customers")),
        "last_order_date": pd.Timestamp("2026-10-01") - pd.to_timedelta(rng.integers(0, 1200, n), unit="D"),
        "recency": rng.integers(1, 41, n),
        "total_orders": orders,
        "total_sales": sales,
        "total_quantity": orders * rng.integers(1, 4, n),
        "total_products": np.minimum(orders, rng.integers(1, 7, n)),
        "lifespan": lifespan,
    })
    cust["avg_order_value"] = cust.total_sales / cust.total_orders
    cust["avg_monthly_spend"] = np.where(cust.lifespan == 0, cust.total_sales,
                                         cust.total_sales / cust.lifespan.replace(0, 1))

    cats = {"Bikes": ["Road Bikes", "Mountain Bikes", "Touring Bikes"],
            "Components": ["Wheels", "Brakes", "Saddles"],
            "Clothing": ["Jerseys", "Shorts", "Gloves"],
            "Accessories": ["Helmets", "Lights", "Locks"]}
    base_price = {"Bikes": 700, "Components": 120, "Clothing": 35, "Accessories": 35}
    rows, key = [], 1
    for c, subs in cats.items():
        for s in subs:
            for j in range(6):
                o = int(rng.integers(5, 260)) * (1 if c == "Bikes" else 2)
                price = base_price[c] * (0.6 + rng.random())
                qty = int(o * (1 + rng.random()))
                life = int(rng.integers(2, 49))
                total = round(o * price)
                rows.append({
                    "product_key": key, "product_name": f"{s[:-1]} {100 + j * 37 + key}",
                    "category": c, "subcategory": s, "cost": round(price * 0.55),
                    "last_sale_date": pd.Timestamp("2026-10-01") - pd.to_timedelta(int(rng.integers(0, 900)), unit="D"),
                    "recency_in_months": int(rng.integers(1, 31)),
                    "product_segment": "High-Performer" if total > 50000 else "Mid-Range" if total >= 10000 else "Low-Performer",
                    "lifespan": life, "total_orders": o, "total_sales": total, "total_quantity": qty,
                    "total_customers": int(o * 0.8), "avg_selling_price": round(total / qty, 1),
                    "avg_order_revenue": total / o, "avg_monthly_revenue": total / life,
                })
                key += 1
    return cust, pd.DataFrame(rows)


# ---------------------------------------------------------------- sidebar
st.sidebar.title("Data source")
source = st.sidebar.radio("Load data from", ["Sample data", "CSV files"])
cust, prod = sample_data()
if source == "CSV files":
    f1 = st.sidebar.file_uploader("report_customer.csv", type="csv")
    f2 = st.sidebar.file_uploader("report_product.csv", type="csv")
    if f1:
        cust = pd.read_csv(f1)
    if f2:
        prod = pd.read_csv(f2)
    if not (f1 and f2):
        st.sidebar.caption("Any file you haven't uploaded falls back to sample data.")

# ---------------------------------------------------------------- theme
PAL = ["#ff8a1f", "#b57edc", "#3b9eff", "#ffb347", "#8e5bb5", "#1e63d6", "#ffd2a0", "#d6b3ee"]
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 12% 8%,rgba(181,126,220,.22) 0,transparent 42%),
       radial-gradient(circle at 92% 92%,rgba(59,158,255,.18) 0,transparent 42%),#050507;}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.block-container{padding-top:1.2rem;max-width:1250px}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.04);
  border:1px solid rgba(181,126,220,.45);border-radius:18px;box-shadow:0 0 18px rgba(255,138,31,.10)}
.banner{background:rgba(255,138,31,.14);border:1px solid rgba(255,138,31,.55);border-radius:10px;
  padding:12px 24px;font-size:44px;line-height:1.1;font-weight:800;letter-spacing:.5px;color:#ff9f40;
  height:182px;display:flex;align-items:center;justify-content:center;text-align:center}
.kpi{background:rgba(255,255,255,.04);border:1px solid rgba(181,126,220,.5);border-radius:18px;
  padding:14px 8px;text-align:center;box-shadow:0 0 18px rgba(59,158,255,.14)}
.kpi b{display:block;font-size:34px;font-weight:700;color:#ff9f40;line-height:1.15}
.kpi span{font-size:14px;color:#cdb8e6}
h1,h2,h3,label,p{color:#fff}
</style>""", unsafe_allow_html=True)


def short(v):
    a = abs(v)
    t = f"{v/1e6:.1f}M" if a >= 1e6 else f"{v/1e3:.1f}K" if a >= 1e3 else f"{v:,.0f}"
    return t.replace(".0K", "K").replace(".0M", "M")


def kpi(col, label, value):
    col.markdown(f'<div class="kpi"><b>{value}</b><span>{label}</span></div>', unsafe_allow_html=True)


def base(fig, title, h=300):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.5, font=dict(size=15, color="white")),
        height=h, margin=dict(l=10, r=10, t=45, b=10), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#efe9f5", size=12),
        hoverlabel=dict(bgcolor="#14101a", font_color="white"))
    return fig


def show(fig):
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def bar(df, cat, val, title, agg="sum", horiz=False, top=None, order=None, h=300):
    d = df.groupby(cat, observed=True)[val].agg(agg).reset_index()
    d = d.set_index(cat).reindex(order).dropna().reset_index() if order else d.sort_values(val, ascending=False)
    if top:
        d = d.head(top)
    colors = [PAL[i % len(PAL)] for i in range(len(d))]
    if horiz:
        d, colors = d.iloc[::-1], colors[::-1]
    lab = [short(v) for v in d[val]]
    fig = go.Figure(go.Bar(
        x=d[val] if horiz else d[cat].astype(str), y=d[cat].astype(str) if horiz else d[val],
        orientation="h" if horiz else "v", marker_color=colors, text=lab,
        textposition="outside", cliponaxis=False, textfont=dict(color="white", size=12),
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>" if horiz else "%{x}: %{y:,.0f}<extra></extra>"))
    hi = max(d[val].max(), 1) * 1.2
    grid = dict(showgrid=True, gridcolor="rgba(255,255,255,.08)", zeroline=False, tickformat="~s")
    if horiz:
        fig.update_xaxes(range=[0, hi], **grid)
        fig.update_yaxes(showgrid=False)
    else:
        fig.update_yaxes(range=[min(0, d[val].min() * 1.2), hi], **grid)
        fig.update_xaxes(showgrid=False)
    return base(fig, title, h)


def donut(df, cat, title, val=None, h=300):
    d = (df.groupby(cat, observed=True)[val].sum() if val else df.groupby(cat, observed=True).size())
    d = d.sort_values(ascending=False)
    fig = go.Figure(go.Pie(
        labels=d.index.astype(str), values=d.values, hole=0.62, sort=False,
        marker=dict(colors=PAL[:len(d)], line=dict(color="#050507", width=2)),
        textinfo="label+percent", textposition="outside", textfont=dict(color="white", size=12),
        hovertemplate="%{label}: %{value:,.0f}<extra></extra>"))
    return base(fig, title, h)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def by_month(df, col):
    if not sel or col not in df:
        return df
    m = pd.to_datetime(df[col], errors="coerce").dt.month
    return df[m.isin([MONTHS.index(x) + 1 for x in sel])]


def opt(col, label, series):
    return col.selectbox(label, ["All"] + sorted(series.dropna().astype(str).unique()))


# ---------------------------------------------------------------- header
t1, t2 = st.columns([2.6, 2])
t1.markdown('<div class="banner">SALES DASHBOARD</div>', unsafe_allow_html=True)
if "months" not in st.session_state:
    st.session_state.months = set()
with t2.container(border=True):
    for r in range(3):
        cols = st.columns(4)
        for i, m in enumerate(MONTHS[r * 4:r * 4 + 4]):
            on = m in st.session_state.months
            if cols[i].button(m, key=f"mb_{m}", type="primary" if on else "secondary",
                              use_container_width=True):
                st.session_state.months ^= {m}
                st.rerun()
sel = list(st.session_state.months)
tab_c, tab_p = st.tabs(["Customers", "Products"])

# ---------------------------------------------------------------- customers
with tab_c:
    f1, f2, _ = st.columns([1, 1, 3])
    sg = opt(f1, "Customer segment", cust.customer_segment)
    ag = opt(f2, "Age group", cust.age_group)
    c = by_month(cust, "last_order_date")
    if sg != "All":
        c = c[c.customer_segment == sg]
    if ag != "All":
        c = c[c.age_group == ag]
    if c.empty:
        st.warning("No customers match these filters.")
    else:
        k = st.columns(4)
        kpi(k[0], "Sum of Sales", short(c.total_sales.sum()))
        kpi(k[1], "Customers", f"{len(c):,}")
        kpi(k[2], "Sum of Orders", short(c.total_orders.sum()))
        kpi(k[3], "Avg Order Value", short(c.total_sales.sum() / max(1, c.total_orders.sum())))

        AGES = ["Under Age", "20-29", "30-39", "40-49", "50 and Above"]
        c = c.assign(lifespan_group=pd.cut(c.lifespan, [-1, 11, 23, 35, 47, 10_000],
                                           labels=["0-11", "12-23", "24-35", "36-47", "48+"]).astype(str))
        a, b, d = st.columns([1.1, 1.1, 1.8])
        with a: show(bar(c, "customer_name", "total_sales", "Top Customers", top=5))
        with b: show(donut(c, "customer_segment", "Customers by Segment"))
        with d: show(bar(c, "age_group", "total_sales", "Sales by Age Group", order=AGES))
        a, b, d = st.columns([1.1, 1.1, 1.5])
        with a: show(bar(c, "customer_segment", "avg_monthly_spend", "Avg Monthly Spend", agg="mean", horiz=True))
        with b: show(donut(c, "age_group", "Orders by Age Group", val="total_orders"))
        with d: show(bar(c, "lifespan_group", "total_sales", "Sales by Lifespan (months)", horiz=True,
                         order=["0-11", "12-23", "24-35", "36-47", "48+"]))
        with st.expander("Customer data"):
            st.dataframe(c.sort_values("total_sales", ascending=False), use_container_width=True, hide_index=True)
            st.download_button("Download CSV", c.to_csv(index=False), "customers.csv")

# ---------------------------------------------------------------- products
with tab_p:
    f1, f2, _ = st.columns([1, 1, 3])
    cg = opt(f1, "Category", prod.category)
    ps = opt(f2, "Product segment", prod.product_segment)
    p = by_month(prod, "last_sale_date")
    if cg != "All":
        p = p[p.category == cg]
    if ps != "All":
        p = p[p.product_segment == ps]
    if p.empty:
        st.warning("No products match these filters.")
    else:
        k = st.columns(4)
        kpi(k[0], "Sum of Sales", short(p.total_sales.sum()))
        kpi(k[1], "Sum of Quantity", short(p.total_quantity.sum()))
        kpi(k[2], "Sum of Orders", short(p.total_orders.sum()))
        kpi(k[3], "Avg Selling Price", short(p.total_sales.sum() / max(1, p.total_quantity.sum())))

        a, b, d = st.columns([1.1, 1.1, 1.8])
        with a: show(bar(p, "product_name", "total_sales", "Top Products", top=5))
        with b: show(donut(p, "category", "Sales by Category", val="total_sales"))
        with d: show(bar(p, "subcategory", "total_sales", "Sales by Sub-Category"))
        a, b, d = st.columns([1.1, 1.1, 1.5])
        with a: show(bar(p, "category", "avg_monthly_revenue", "Avg Monthly Revenue", agg="mean", horiz=True))
        with b: show(donut(p, "product_segment", "Quantity by Segment", val="total_quantity"))
        with d: show(bar(p, "subcategory", "total_quantity", "Top Sub-Categories by Units", horiz=True, top=5))
        with st.expander("Product data"):
            st.dataframe(p.sort_values("total_sales", ascending=False), use_container_width=True, hide_index=True)
            st.download_button("Download CSV", p.to_csv(index=False), "products.csv")