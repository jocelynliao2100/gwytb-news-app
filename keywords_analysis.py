import streamlit as st
import pandas as pd
import jieba
import jieba.analyse
from datetime import datetime
from collections import Counter

# 自訂關鍵字群組
KEYWORD_CATEGORIES = {
    "台獨相關": ["台獨", "民進黨", "賴清德", "蔡英文"],
    "國民黨相關": ["國民黨", "馬英九"],
    "美國相關": ["美國", "美方"],
    "經濟發展與交流相關": ["發展", "台商", "青年"],
    "其他": ["九二共識", "兩國論", "2758"]
}

ALL_KEYWORDS = [kw for group in KEYWORD_CATEGORIES.values() for kw in group]


def render_keywords_analysis():
    st.title("🔍 國台辦新聞稿關鍵字分析（CSV 上傳版）")

    uploaded_file = st.file_uploader(
        "📂 請上傳整理後的 CSV 檔案（需包含「日期」與「標題」欄位）",
        type="csv"
    )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ 無法讀取檔案：{e}")
            return

        if not {"日期", "標題"}.issubset(df.columns):
            st.error("❗ 檔案中缺少必要欄位，請確認包含「日期」與「標題」")
            return

        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        df = df.dropna(subset=["日期"])
        df["月份"] = df["日期"].dt.to_period("M").dt.to_timestamp()

        st.success(f"✅ 已載入 {len(df)} 筆新聞資料")
        st.dataframe(df)

        # 全文關鍵字統計
        st.markdown("### 🔠 所有新聞標題關鍵字（Top 20）")
        full_text = " ".join(df["標題"].tolist())
        top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
        st.bar_chart(keyword_df.set_index("關鍵字"))

        # 關鍵字群組分析
        st.markdown("### 📊 指定關鍵字群組出現趨勢分析")

        # 計算每個月每個關鍵字的出現次數
        keyword_monthly = []
        for month, group in df.groupby("月份"):
            titles = " ".join(group["標題"].tolist())
            for keyword in ALL_KEYWORDS:
                count = titles.count(keyword)
                keyword_monthly.append({"月份": month, "關鍵字": keyword, "出現次數": count})

        km_df = pd.DataFrame(keyword_monthly)

        # 依群組顯示圖表與出現最多月份新聞
        for group_name, keywords in KEYWORD_CATEGORIES.items():
            st.subheader(f"📌 {group_name}")
            filtered = km_df[km_df["關鍵字"].isin(keywords)]
            pivot = filtered.pivot(index="月份", columns="關鍵字", values="出現次數").fillna(0)
            st.line_chart(pivot)

            # 統計各關鍵字出現最多的月份
            for keyword in keywords:
                subset = km_df[km_df["關鍵字"] == keyword]
                top_months = subset.sort_values("出現次數", ascending=False).head(5)
                st.markdown(f"**🔍 {keyword}：出現次數最多的前五個月份：**")
                st.table(top_months[["月份", "出現次數"]])

                # 顯示該月份的新聞標題
                for _, row in top_months.iterrows():
                    m = row["月份"]
                    m_df = df[df["月份"] == m]
                    matched_titles = [t for t in m_df["標題"] if keyword in t]
                    with st.expander(f"📰 {m.strftime('%Y-%m')} 出現 {keyword} 的新聞標題（共 {len(matched_titles)} 筆）"):
                        for t in matched_titles:
                            st.markdown(f"- {t}")
    else:
        st.info("請上傳 CSV 檔案以開始分析。")
