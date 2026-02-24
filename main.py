import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="GAAVN Analytics Dashboard", layout="wide")
st.title("📊 GAAVN Data Science Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:

    excel_file = pd.ExcelFile(uploaded_file)
    sheet_choice = st.selectbox("Select sheet", excel_file.sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=sheet_choice)

    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

    if sheet_choice == "Data":
       
        df['Total_Cost'] = (df['Milk_Input_Ltrs']*df['Milk_Purchase_Price_per_Litre']) + \
                           df['Ingredient_Cost_RS'] + df['Labour_Cost_RS'] + df['Utility_Cost_RS']
        df['Total_Sales'] = df['Paneer_Output_Kg'] * df["Selling_Price_per_Kg_RS"]
        df['Yield_Percent'] = (df['Paneer_Output_Kg']/df['Milk_Input_Ltrs'])*100
        df['Cost_per_kg'] = df['Total_Cost']/df['Paneer_Output_Kg']
        df['Gross_Margin'] = df['Total_Sales'] - df['Total_Cost']

     
        df['Date'] = pd.to_datetime(df['Date'].apply(lambda x: f"{x}-2024"), format='%d-%m-%Y')

        st.markdown("---")
        st.subheader("📈 Yield & Margin Trends")

        
        mean_yield = df['Yield_Percent'].mean()
        std_yield = df['Yield_Percent'].std()
        lb_yield, ub_yield = mean_yield - std_yield, mean_yield + std_yield

        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(df["Date"], df["Yield_Percent"], marker="o")
        ax.axhline(lb_yield, linestyle="--", color="red")
        ax.axhline(ub_yield, linestyle="--", color="red")
        ax.set_title("Yield % Over Time")
        st.pyplot(fig)

     
        mean_margin = df['Gross_Margin'].mean()
        std_margin = df['Gross_Margin'].std()
        lb_margin, ub_margin = mean_margin - std_margin, mean_margin + std_margin

        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(df["Date"], df["Gross_Margin"], marker="o")
        ax.axhline(lb_margin, linestyle="--", color="red")
        ax.axhline(ub_margin, linestyle="--", color="red")
        ax.set_title("Gross Margin Over Time")
        st.pyplot(fig)

        # Abnormal flags
        df['Abnormal_Yield'] = df['Yield_Percent'].apply(lambda x: "Abnormal" if (x<lb_yield or x>ub_yield) else "Normal")
        df['Abnormal_Gross_Margin'] = df['Gross_Margin'].apply(lambda x: "Abnormal" if (x<lb_margin or x>ub_margin) else "Normal")

        st.subheader("🚨 Abnormal Days")
        st.dataframe(df[df['Abnormal_Yield']=="Abnormal"][['Date','Yield_Percent','Abnormal_Yield']])
        st.dataframe(df[df['Abnormal_Gross_Margin']=="Abnormal"][['Date','Gross_Margin','Abnormal_Gross_Margin']])

        st.markdown("---")
        st.subheader("📉 Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(df.select_dtypes(include='number').corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

        st.subheader("🔍 Relationships")
        scatter_choice = st.selectbox("Select relationship", ["Fat vs Yield", "SNF vs Yield", "SOP vs Yield", "Capacity vs Yield",
                                                              "Capacity_Utilization vs SOP"])
        fig, ax = plt.subplots(figsize=(8,6))

        if scatter_choice == "Fat vs Yield":
            mean_yield = df['Yield_Percent'].mean()
            std_yield = df['Yield_Percent'].std()
            lb_yield, ub_yield = mean_yield - std_yield, mean_yield + std_yield

            sns.scatterplot(x='Fat_Percent', y='Yield_Percent', data=df, ax=ax)
            ax.axhline(lb_yield, linestyle="--", color="red")
            ax.axhline(ub_yield, linestyle="--", color="red")

        elif scatter_choice == "SNF vs Yield":
            mean_yield = df['Yield_Percent'].mean()
            std_yield = df['Yield_Percent'].std()
            lb_yield, ub_yield = mean_yield - std_yield, mean_yield + std_yield

            sns.regplot(x='SNF_Percent', y='Yield_Percent', data=df, ax=ax)
            ax.axhline(lb_yield, linestyle="--", color="red")
            ax.axhline(ub_yield, linestyle="--", color="red")

        elif scatter_choice == "SOP vs Yield":
            mean_yield = df['Yield_Percent'].mean()
            std_yield = df['Yield_Percent'].std()
            lb_yield, ub_yield = mean_yield - std_yield, mean_yield + std_yield

            sns.regplot(x='SOP_Adherence_Score', y='Yield_Percent', data=df, ax=ax)
            ax.axhline(lb_yield, linestyle="--", color="red")
            ax.axhline(ub_yield, linestyle="--", color="red")
            
        elif scatter_choice == "Capacity_Utilization vs SOP":
            sns.scatterplot(x='SOP_Adherence_Score', 
                    y='Capacity_Utilization_Percent', 
                    data=df, ax=ax)
            ax.set_title("Capacity Utilization % vs SOP Adherence Score")
            ax.set_xlabel("SOP Adherence Score")
            ax.set_ylabel("Capacity Utilization %")
            ax.grid(True)

        else: 
            mean_yield = df['Yield_Percent'].mean()
            std_yield = df['Yield_Percent'].std()
            lb_yield, ub_yield = mean_yield - std_yield, mean_yield + std_yield

            sns.scatterplot(x='Capacity_Utilization_Percent', y='Yield_Percent', data=df, ax=ax)
            ax.axhline(lb_yield, linestyle="--", color="red")
            ax.axhline(ub_yield, linestyle="--", color="red")

        st.pyplot(fig)

else:
    st.info("Upload an Excel file to begin")
