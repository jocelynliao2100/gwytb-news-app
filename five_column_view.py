import streamlit as st
import pandas as pd

def render_five_column_analysis():
    st.subheader("📂 五大欄目新聞稿分析")
    
    uploaded_file = st.file_uploader(
        "📥 請上傳整理後的 .csv 檔案（需包含「日期」「標題」「欄目」欄位）",
        type="csv"
    )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ 檔案讀取失敗：{e}")
            return

        required_cols = {"日期", "標題", "欄目"}
        if not required_cols.issubset(df.columns):
            st.error("❗ 檔案中缺少必要欄位。請確認包含以下欄位：日期、標題、欄目")
            return

        # 資料處理
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        df = df.dropna(subset=["日期"])
        df["月份"] = df["日期"].dt.to_period("M").dt.to_timestamp()

        st.success(f"✅ 成功載入 {len(df)} 筆新聞，涵蓋 {df['欄目'].nunique()} 個欄目")
        st.dataframe(df)

        # 各欄目新聞總量
        st.markdown("### 📊 各欄目新聞總量統計")
        st.bar_chart(df["欄目"].value_counts())

        # 各欄目新聞隨月份變化
        st.markdown("### 📈 各欄目新聞時間趨勢（按月）")
        pivot = df.groupby(["月份", "欄目"]).size().reset_index(name="數量")
        pivot_wide = pivot.pivot(index="月份", columns="欄目", values="數量").fillna(0)
        st.line_chart(pivot_wide)

    else:
        st.info("請上傳一份整理後的 CSV 檔案以開始分析。")
