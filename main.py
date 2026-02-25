import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="GAAVN Analytics Dashboard", layout="wide")
st.title("📊 GAAVN Data Science Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Load all sheets
    excel_file = pd.ExcelFile(uploaded_file)
    sheet_choice = st.selectbox("Select sheet", excel_file.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_choice)

    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

    if sheet_choice == "Data":
        # Derived metrics
        df['Total_Cost'] = (df['Milk_Input_Ltrs']*df['Milk_Purchase_Price_per_Litre']) + \
                           df['Ingredient_Cost_RS'] + df['Labour_Cost_RS'] + df['Utility_Cost_RS']
        df['Total_Sales'] = df['Paneer_Output_Kg'] * df["Selling_Price_per_Kg_RS"]
        df['Yield_Percent'] = (df['Paneer_Output_Kg']/df['Milk_Input_Ltrs'])*100
        df['Cost_per_kg'] = df['Total_Cost']/df['Paneer_Output_Kg']
        df['Gross_Margin'] = df['Total_Sales'] - df['Total_Cost']

        # Convert Date
        df['Date'] = pd.to_datetime(df['Date'].apply(lambda x: f"{x}-2024"), format='%d-%m-%Y')

        # --- KPI Section ---
        st.markdown("---")
        st.subheader("📌 Key Performance Indicators (KPIs)")

        total_revenue = df['Total_Sales'].sum()
        avg_daily_profit = df['Gross_Margin'].mean()
        profit_per_litre = (df['Gross_Margin'].sum() / df['Milk_Input_Ltrs'].sum())
        avg_yield_efficiency = df['Yield_Percent'].mean()
        avg_capacity_utilization = df['Capacity_Utilization_Percent'].mean()
        avg_sop_adherence = df['SOP_Adherence_Score'].mean()

        kpi_data = {
            "KPI": [
                "Total Revenue (60 days)",
                "Avg Daily Profit",
                "Profit per Litre",
                "Avg Yield Efficiency",
                "Avg Capacity Utilization",
                "Avg SOP Adherence"
            ],
            "Value": [
                f"₹{total_revenue:,.0f}",
                f"₹{avg_daily_profit:,.0f}",
                f"₹{profit_per_litre:,.2f}",
                f"{avg_yield_efficiency:.2f}%",
                f"{avg_capacity_utilization:.2f}%",
                f"{avg_sop_adherence:.2f}%"
            ]
            # ,
            # "What it shows": [
            #     "Business size",
            #     "Sustainability",
            #     "Unit economics",
            #     "Process health",
            #     "Plant usage",
            #     "Operational discipline"
            # ]
        }

        kpi_df = pd.DataFrame(kpi_data)
        st.table(kpi_df)


        st.markdown("---")
        st.subheader("📈 Yield & Margin Trends")
  
        
        st.markdown("---")
        st.subheader("📈 Daily Trend Charts")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.plot(df["Date"], df["Gross_Margin"], marker="o", color="green")
            ax.axhline(0, linestyle="--", color="red")
            ax.set_title("📈 Daily Profit Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Profit (Rs)")
            st.pyplot(fig)

    
        with col2:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.plot(df["Date"], df["Yield_Percent"], marker="o", color="blue")
            ax.set_title("📈 Yield Efficiency Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Yield %")
            st.pyplot(fig)

        col3, col4 = st.columns(2)

        with col3:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.plot(df["Date"], df["Capacity_Utilization_Percent"], marker="o", color="orange")
            ax.axhline(100, linestyle="--", color="red")
            ax.set_title("📈 Capacity Utilization Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Utilization %")
            st.pyplot(fig)

    
        with col4:
            fig, ax = plt.subplots(figsize=(6,4))
            ax.plot(df["Date"], df["SOP_Adherence_Score"], marker="o", color="purple")
            ax.set_title("📈 SOP Adherence Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("SOP Adherence Score")
            st.pyplot(fig)


        st.markdown("### 📈 Utility Cost per Litre Trend (Optional)")
        df['Utility_Cost_per_Litre'] = df['Utility_Cost_RS'] / df['Milk_Input_Ltrs']
        fig, ax = plt.subplots(figsize=(12,4))
        ax.plot(df["Date"], df["Utility_Cost_per_Litre"], marker="o", color="brown")
        ax.set_title("📈 Utility Cost per Litre Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cost per Litre (Rs)")
        st.pyplot(fig)
        

        mean_yield = df['Yield_Percent'].mean()
        std_yield = df['Yield_Percent'].std()
        lower_bound = mean_yield - std_yield
        upper_bound = mean_yield + std_yield

        def yield_flag(x, lb, ub):
            if x < lb:
                return "Abnormal (Lower than Normal)"
            elif x > ub:
                return "Abnormal (Higher than Normal)"
            else:
                return "Normal"

        df['Abnormal_Yield'] = df['Yield_Percent'].apply(lambda x: yield_flag(x, lower_bound, upper_bound))

        st.markdown("---")
        st.subheader("🚨 Abnormal Yield Days")

        abnormal_yield_df = df[df['Abnormal_Yield'] != "Normal"][['Date','Yield_Percent','Abnormal_Yield']]
        st.dataframe(abnormal_yield_df)
