import streamlit as st
import pandas as pd

st.set_page_config(page_title="五大欄目新聞稿分析", layout="wide")
st.header("📂 五大欄目新聞稿數量與時間分析")

uploaded_file = st.file_uploader("📂 請上傳欄目新聞稿整理後的 CSV 檔案（含「日期、標題、欄目」欄）", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if {"日期", "標題", "欄目"}.issubset(df.columns):
        df["日期"] = pd.to_datetime(df["日期"])
        df["月份"] = df["日期"].dt.to_period("M").dt.to_timestamp()

        st.success(f"✅ 共載入 {len(df)} 筆新聞，涵蓋 {df['欄目'].nunique()} 個欄目")
        st.dataframe(df)

        st.subheader("📊 各欄目新聞總數")
        st.bar_chart(df["欄目"].value_counts())

        st.subheader("📈 各欄目新聞隨時間變化")
        pivot = df.groupby(["月份", "欄目"]).size().reset_index(name="數量")
        pivot_wide = pivot.pivot(index="月份", columns="欄目", values="數量").fillna(0)
        st.line_chart(pivot_wide)
    else:
        st.error("❗ 資料缺少必要欄位：請確認包含「日期」「標題」「欄目」三欄。")
else:
    st.info("請上傳一份整理後的 .csv 檔案以進行分析。")
