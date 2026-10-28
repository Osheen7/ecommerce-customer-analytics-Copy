import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="E-Commerce Customer Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 36px;
    font-weight: 700;
}

.subtitle {
    font-size: 17px;
    color: #666;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    transactions = pd.read_csv(
        "transactions.csv",
        low_memory=False
    )

    customer_segments = pd.read_csv(
        "customer_segments.csv",
        low_memory=False
    )

    customer_clv = pd.read_csv(
        "customer_clv.csv",
        low_memory=False
    )

    customer_churn = pd.read_csv(
        "customer_churn.csv",
        low_memory=False
    )

    if "purchase_date" in transactions.columns:
        transactions["purchase_date"] = pd.to_datetime(
            transactions["purchase_date"],
            errors="coerce"
        )

    return (
        transactions,
        customer_segments,
        customer_clv,
        customer_churn
    )


transactions, customer_segments, customer_clv, customer_churn = load_data()


# ============================================================
# FIND REVENUE COLUMN
# ============================================================

if "revenue" in transactions.columns:

    revenue_column = "revenue"

elif "final_price" in transactions.columns:

    revenue_column = "final_price"

else:

    revenue_column = None


# ============================================================
# BASIC CALCULATIONS
# ============================================================

if revenue_column:

    total_revenue = transactions[revenue_column].sum()

    average_transaction = transactions[
        revenue_column
    ].mean()

else:

    total_revenue = 0
    average_transaction = 0


total_transactions = len(transactions)


if "user_id" in transactions.columns:

    total_customers = transactions[
        "user_id"
    ].nunique()

else:

    total_customers = len(
        customer_segments
    )


if "is_returned" in transactions.columns:

    return_rate = (
        transactions["is_returned"].mean()
        * 100
    )

else:

    return_rate = 0


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛒 E-Commerce Analytics")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Dashboard Pages",
    [
        "🏠 Executive Overview",
        "👥 Customer Segmentation",
        "📉 Churn Analytics",
        "💰 Customer Lifetime Value",
        "🛍️ Product Intelligence",
        "💡 Key Insights"
    ]
)

st.sidebar.markdown("---")

st.sidebar.write(
    "**Project:**"
)

st.sidebar.write(
    "E-Commerce Customer Intelligence "
    "& Analytics System"
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Python • Pandas • Plotly • Streamlit"
)


# ============================================================
# PAGE 1
# EXECUTIVE OVERVIEW
# ============================================================

if page == "🏠 Executive Overview":

    st.markdown(
        '<div class="main-title">'
        '🛒 E-Commerce Customer Intelligence & Analytics System'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'End-to-end analysis of customer behavior, sales, '
        'churn, lifetime value and product performance.'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # KPI ROW

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "💰 Total Revenue",
            f"₹{total_revenue / 1_000_000_000:.2f}B"
        )

    with col2:

        st.metric(
            "👥 Customers",
            f"{total_customers:,}"
        )

    with col3:

        st.metric(
            "🛍️ Transactions",
            f"{total_transactions / 1_000_000:.1f}M"
        )

    with col4:

        st.metric(
            "💳 Avg Transaction",
            f"₹{average_transaction:,.2f}"
        )

    with col5:

        st.metric(
            "↩️ Return Rate",
            f"{return_rate:.2f}%"
        )

    st.divider()

    # REVENUE TREND

    st.subheader("📈 Monthly Revenue Trend")

    if (
        "purchase_date" in transactions.columns
        and revenue_column
    ):

        monthly_revenue = (
            transactions
            .dropna(subset=["purchase_date"])
            .set_index("purchase_date")
            .resample("ME")[revenue_column]
            .sum()
            .reset_index()
        )

        fig = px.line(
            monthly_revenue,
            x="purchase_date",
            y=revenue_column,
            markers=True
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (₹)",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # CATEGORY + PAYMENT

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Revenue by Category")

        if (
            "category" in transactions.columns
            and revenue_column
        ):

            category_data = (
                transactions
                .groupby("category")[revenue_column]
                .sum()
                .sort_values(
                    ascending=False
                )
                .reset_index()
            )

            fig = px.bar(
                category_data,
                x="category",
                y=revenue_column,
                text_auto=".2s"
            )

            fig.update_layout(
                height=420,
                xaxis_title="Category",
                yaxis_title="Revenue (₹)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with col2:

        st.subheader("💳 Payment Method Usage")

        if "payment_method" in transactions.columns:

            payment_data = (
                transactions[
                    "payment_method"
                ]
                .value_counts()
                .reset_index()
            )

            payment_data.columns = [
                "Payment Method",
                "Transactions"
            ]

            fig = px.pie(
                payment_data,
                names="Payment Method",
                values="Transactions",
                hole=0.45
            )

            fig.update_layout(
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# PAGE 2
# CUSTOMER SEGMENTATION
# ============================================================

elif page == "👥 Customer Segmentation":

    st.title("👥 Customer Segmentation")

    st.write(
        "RFM-based analysis of customer purchasing behavior."
    )

    st.divider()

    # KPI

    col1, col2, col3, col4 = st.columns(4)

    if "Recency" in customer_segments.columns:

        avg_recency = (
            customer_segments["Recency"].mean()
        )

    else:

        avg_recency = 0

    if "Frequency" in customer_segments.columns:

        avg_frequency = (
            customer_segments["Frequency"].mean()
        )

    else:

        avg_frequency = 0

    if "Monetary" in customer_segments.columns:

        avg_monetary = (
            customer_segments["Monetary"].mean()
        )

    else:

        avg_monetary = 0

    with col1:

        st.metric(
            "👥 Customers",
            f"{len(customer_segments):,}"
        )

    with col2:

        st.metric(
            "📅 Avg Recency",
            f"{avg_recency:.1f} days"
        )

    with col3:

        st.metric(
            "🔄 Avg Frequency",
            f"{avg_frequency:.2f}"
        )

    with col4:

        st.metric(
            "💰 Avg Monetary",
            f"₹{avg_monetary:,.2f}"
        )

    st.divider()

    # SEGMENTS

    if "Segment" in customer_segments.columns:

        segment_counts = (
            customer_segments["Segment"]
            .value_counts()
            .reset_index()
        )

        segment_counts.columns = [
            "Segment",
            "Customers"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Customer Segment Distribution"
            )

            fig = px.bar(
                segment_counts,
                x="Segment",
                y="Customers",
                text="Customers"
            )

            fig.update_layout(
                height=430,
                xaxis_tickangle=-25
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "Customer Segment Share"
            )

            fig = px.pie(
                segment_counts,
                names="Segment",
                values="Customers",
                hole=0.45
            )

            fig.update_layout(
                height=430
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        # SEGMENT PERFORMANCE

        st.subheader(
            "📊 Segment Performance"
        )

        segment_columns = [
            col
            for col in [
                "Recency",
                "Frequency",
                "Monetary"
            ]
            if col in customer_segments.columns
        ]

        if segment_columns:

            segment_summary = (
                customer_segments
                .groupby("Segment")[
                    segment_columns
                ]
                .mean()
                .round(2)
                .reset_index()
            )

            st.dataframe(
                segment_summary,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # RFM SCATTER

        if (
            "Recency" in customer_segments.columns
            and "Monetary" in customer_segments.columns
            and "Frequency" in customer_segments.columns
        ):

            st.subheader(
                "📈 RFM Customer Behavior"
            )

            sample_size = min(
                15000,
                len(customer_segments)
            )

            sample_data = (
                customer_segments
                .sample(
                    sample_size,
                    random_state=42
                )
            )

            fig = px.scatter(
                sample_data,
                x="Recency",
                y="Monetary",
                size="Frequency",
                color="Segment"
                if "Segment"
                in sample_data.columns
                else None,
                hover_data=[
                    "user_id"
                ]
                if "user_id"
                in sample_data.columns
                else None,
                opacity=0.6
            )

            fig.update_layout(
                height=550
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# PAGE 3
# CHURN ANALYTICS
# ============================================================

elif page == "📉 Churn Analytics":

    st.title("📉 Customer Churn Analytics")

    st.write(
        "Identify customer churn patterns and the strongest "
        "predictive features from the Random Forest model."
    )

    st.divider()

    # CHURN COUNTS

    if "Churn" in customer_churn.columns:

        churn_counts = (
            customer_churn["Churn"]
            .value_counts()
            .sort_index()
        )

        active_customers = (
            churn_counts.get(0, 0)
        )

        churned_customers = (
            churn_counts.get(1, 0)
        )

        total_churn_records = (
            active_customers
            + churned_customers
        )

        if total_churn_records > 0:

            churn_rate = (
                churned_customers
                / total_churn_records
            ) * 100

        else:

            churn_rate = 0

        # KPI

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🟢 Active Customers",
                f"{active_customers:,}"
            )

        with col2:

            st.metric(
                "🔴 Churned Customers",
                f"{churned_customers:,}"
            )

        with col3:

            st.metric(
                "⚠️ Churn Rate",
                f"{churn_rate:.2f}%"
            )

        st.divider()

        # CHURN DISTRIBUTION

        churn_data = pd.DataFrame({
            "Status": [
                "Active Customers",
                "Churned Customers"
            ],
            "Customers": [
                active_customers,
                churned_customers
            ]
        })

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Customer Churn Distribution"
            )

            fig = px.bar(
                churn_data,
                x="Status",
                y="Customers",
                text="Customers"
            )

            fig.update_layout(
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "Churn Share"
            )

            fig = px.pie(
                churn_data,
                names="Status",
                values="Customers",
                hole=0.45
            )

            fig.update_layout(
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.warning(
            "The Churn column was not found in customer_churn.csv."
        )

    st.divider()

    # RANDOM FOREST FEATURE IMPORTANCE

    st.subheader(
        "🌲 Random Forest Feature Importance"
    )

    feature_importance = pd.DataFrame({
        "Feature": [
            "Avg_Transaction_Value",
            "Monetary",
            "Recency",
            "Avg_Rating",
            "Avg_Shipping_Time",
            "Return_Rate",
            "Frequency"
        ],
        "Importance": [
            0.279769,
            0.279722,
            0.262093,
            0.115168,
            0.045705,
            0.010087,
            0.007456
        ]
    })

    feature_importance = (
        feature_importance
        .sort_values(
            "Importance",
            ascending=True
        )
    )

    fig = px.bar(
        feature_importance,
        x="Importance",
        y="Feature",
        orientation="h",
        text="Importance"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Importance",
        yaxis_title="Feature"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Average Transaction Value, Monetary Value and "
        "Recency were the strongest features in the "
        "Random Forest churn model."
    )


# ============================================================
# PAGE 4
# CUSTOMER LIFETIME VALUE
# ============================================================

elif page == "💰 Customer Lifetime Value":

    st.title("💰 Customer Lifetime Value")

    st.write(
        "Measure the long-term economic value of customers."
    )

    st.divider()

    # CLV VALUES

    if "CLV" in customer_clv.columns:

        average_clv = (
            customer_clv["CLV"].mean()
        )

        maximum_clv = (
            customer_clv["CLV"].max()
        )

    else:

        average_clv = 0
        maximum_clv = 0

    if (
        "Customer_Lifespan_Days"
        in customer_clv.columns
    ):

        average_lifespan = (
            customer_clv[
                "Customer_Lifespan_Days"
            ].mean()
        )

    else:

        average_lifespan = 0

    if "CLV_Segment" in customer_clv.columns:

        high_clv_customers = (
            customer_clv["CLV_Segment"]
            .eq("High CLV")
            .sum()
        )

    else:

        high_clv_customers = 0

    # KPI

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Average CLV",
            f"₹{average_clv:,.2f}"
        )

    with col2:

        st.metric(
            "High CLV Customers",
            f"{high_clv_customers:,}"
        )

    with col3:

        st.metric(
            "Maximum CLV",
            f"₹{maximum_clv:,.2f}"
        )

    with col4:

        st.metric(
            "Avg Customer Lifespan",
            f"{average_lifespan:.1f} days"
        )

    st.divider()

    # CLV SEGMENTS

    if "CLV_Segment" in customer_clv.columns:

        clv_counts = (
            customer_clv["CLV_Segment"]
            .value_counts()
            .reset_index()
        )

        clv_counts.columns = [
            "CLV Segment",
            "Customers"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "CLV Segment Distribution"
            )

            fig = px.bar(
                clv_counts,
                x="CLV Segment",
                y="Customers",
                text="Customers"
            )

            fig.update_layout(
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "CLV Segment Share"
            )

            fig = px.pie(
                clv_counts,
                names="CLV Segment",
                values="Customers",
                hole=0.45
            )

            fig.update_layout(
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        # CLV PERFORMANCE

        st.subheader(
            "📊 CLV Segment Performance"
        )

        clv_columns = [
            col
            for col in [
                "Total_Revenue",
                "Purchase_Frequency",
                "Avg_Transaction_Value",
                "CLV",
                "Customer_Lifespan_Days"
            ]
            if col in customer_clv.columns
        ]

        if clv_columns:

            clv_summary = (
                customer_clv
                .groupby("CLV_Segment")[
                    clv_columns
                ]
                .mean()
                .round(2)
                .reset_index()
            )

            st.dataframe(
                clv_summary,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # CLV DISTRIBUTION

        if "CLV" in customer_clv.columns:

            st.subheader(
                "📈 CLV Distribution"
            )

            fig = px.histogram(
                customer_clv,
                x="CLV",
                nbins=60
            )

            fig.update_layout(
                height=450,
                xaxis_title="Customer Lifetime Value",
                yaxis_title="Customers"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# PAGE 5
# PRODUCT INTELLIGENCE
# ============================================================

elif page == "🛍️ Product Intelligence":

    st.title("🛍️ Product Intelligence")

    st.write(
        "Explore product performance and purchasing behavior."
    )

    st.divider()

    # PRODUCT KPIs

    if "product_id" in transactions.columns:

        unique_products = (
            transactions["product_id"].nunique()
        )

    else:

        unique_products = 0

    if "category" in transactions.columns:

        total_categories = (
            transactions["category"].nunique()
        )

    else:

        total_categories = 0

    if "brand" in transactions.columns:

        total_brands = (
            transactions["brand"].nunique()
        )

    else:

        total_brands = 0

    if (
        "user_id" in transactions.columns
        and "product_id"
        in transactions.columns
    ):

        avg_products_customer = (
            transactions
            .groupby("user_id")["product_id"]
            .nunique()
            .mean()
        )

    else:

        avg_products_customer = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Unique Products",
            f"{unique_products:,}"
        )

    with col2:

        st.metric(
            "Categories",
            f"{total_categories:,}"
        )

    with col3:

        st.metric(
            "Brands",
            f"{total_brands:,}"
        )

    with col4:

        st.metric(
            "Avg Products / Customer",
            f"{avg_products_customer:.2f}"
        )

    st.divider()

    # TOP PRODUCTS

    if (
        "product_id" in transactions.columns
        and revenue_column
    ):

        top_products = (
            transactions
            .groupby("product_id")[revenue_column]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        st.subheader(
            "🏆 Top 10 Products by Revenue"
        )

        fig = px.bar(
            top_products,
            x=revenue_column,
            y="product_id",
            orientation="h",
            text_auto=".2s"
        )

        fig.update_layout(
            height=500,
            xaxis_title="Revenue (₹)",
            yaxis_title="Product"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # CATEGORY

    if (
        "category" in transactions.columns
        and revenue_column
    ):

        category_revenue = (
            transactions
            .groupby("category")[revenue_column]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        st.subheader(
            "📦 Revenue by Category"
        )

        fig = px.bar(
            category_revenue,
            x="category",
            y=revenue_column,
            text_auto=".2s"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # DEVICE

    if "device" in transactions.columns:

        st.subheader(
            "📱 Transactions by Device"
        )

        device_data = (
            transactions["device"]
            .value_counts()
            .reset_index()
        )

        device_data.columns = [
            "Device",
            "Transactions"
        ]

        fig = px.pie(
            device_data,
            names="Device",
            values="Transactions",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 6
# KEY INSIGHTS
# ============================================================

elif page == "💡 Key Insights":

    st.title(
        "💡 Key Business Insights"
    )

    st.write(
        "The most important findings from the "
        "E-Commerce Customer Intelligence project."
    )

    st.divider()

    # OVERALL PERFORMANCE

    st.subheader(
        "📊 Overall Business Performance"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Revenue",
            "₹9.94B"
        )

    with col2:

        st.metric(
            "Customers Analyzed",
            "603,815"
        )

    with col3:

        st.metric(
            "Transactions",
            "1 Million"
        )

    st.divider()

    # KEY FINDINGS

    st.subheader(
        "🔍 Key Findings"
    )

    findings = [
        (
            "💰 Strong Revenue Generation",
            "The platform generated approximately "
            "₹9.94 billion from 1 million transactions."
        ),

        (
            "👥 Large Customer Base",
            "603,815 unique customers were analyzed, "
            "providing a strong base for customer "
            "segmentation and personalization."
        ),

        (
            "⚠️ High Customer Churn",
            "The analysis identified a churn rate of "
            "approximately 75.88%, highlighting a major "
            "customer-retention opportunity."
        ),

        (
            "🎯 Important Churn Predictors",
            "Average Transaction Value, Monetary Value "
            "and Recency were the strongest features "
            "in the Random Forest churn model."
        ),

        (
            "💎 High-Value Customers",
            "High-CLV customers showed substantially "
            "higher purchase frequency and longer "
            "customer lifespans."
        ),

        (
            "🛍️ Product Opportunities",
            "Product-level analysis can support "
            "cross-selling, upselling and personalized "
            "product recommendations."
        )
    ]

    for title, description in findings:

        st.markdown(
            f"### {title}"
        )

        st.write(
            description
        )

        st.markdown("---")

    # BUSINESS RECOMMENDATIONS

    st.subheader(
        "🚀 Business Recommendations"
    )

    recommendations = pd.DataFrame({

        "Business Area": [
            "Customer Retention",
            "High-Value Customers",
            "Personalization",
            "Product Strategy",
            "Delivery Experience",
            "Returns Management"
        ],

        "Recommended Action": [

            "Target high-risk and inactive customers "
            "with personalized retention campaigns.",

            "Create loyalty programs and exclusive "
            "benefits for high-CLV customers.",

            "Use customer segments to provide "
            "personalized offers and recommendations.",

            "Promote high-performing products and "
            "use recommendations for cross-selling.",

            "Improve delivery performance to strengthen "
            "customer satisfaction.",

            "Investigate frequently returned products "
            "to identify quality or expectation issues."
        ]
    })

    st.dataframe(
        recommendations,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # FINAL TAKEAWAY

    st.subheader(
        "🎯 Project Takeaway"
    )

    st.success(
        "This project demonstrates how raw e-commerce "
        "transaction data can be transformed into "
        "actionable business intelligence using "
        "RFM analysis, customer segmentation, "
        "Customer Lifetime Value analysis, churn "
        "prediction and product intelligence."
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "E-Commerce Customer Intelligence & Analytics System"
)

st.sidebar.caption(
    "Built with Python • Pandas • Plotly • Streamlit"
)