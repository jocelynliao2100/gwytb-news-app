import streamlit as st
import pandas as pd
from docx import Document
import jieba.analyse
import re
from datetime import datetime

# 設定頁面
st.set_page_config(page_title="關鍵字分析", page_icon="🔍", layout="wide")
st.title("🔍 國台辦新聞稿關鍵字分析")

# 上傳 Word 檔
uploaded_files = st.file_uploader(
    "📂 請上傳一個或多個 Word 檔案（格式如：[2024-04-01] 標題內容）",
    type="docx",
    accept_multiple_files=True
)

if uploaded_files:
    records = []

    for file in uploaded_files:
        doc = Document(file)
        for para in doc.paragraphs:
            text = para.text.strip()
            match = re.match(r"\[(\d{4}-\d{2}-\d{2})\](.*)", text)
            if match:
                date = match.group(1)
                title = match.group(2).strip()
                records.append({"日期": date, "標題": title})

    if not records:
        st.warning("⚠️ 未擷取到符合格式的標題，請確認段落格式為：[YYYY-MM-DD] 標題內容")
    else:
        # 建立 DataFrame 並轉換時間格式
        df = pd.DataFrame(records)
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        df = df.dropna(subset=["日期"])
        df["月份"] = df["日期"].dt.to_period("M").dt.to_timestamp()

        st.success(f"✅ 已擷取 {len(df)} 筆新聞標題")
        st.dataframe(df)

        # 全文關鍵字統計
        st.markdown("### 🔠 所有新聞標題關鍵字（Top 20）")
        full_text = " ".join(df["標題"].tolist())
        top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
        st.bar_chart(keyword_df.set_index("關鍵字"))

        # 各月份熱門關鍵字
        st.markdown("### 📅 各月份熱門關鍵字（Top 5）")
        for month in sorted(df["月份"].unique()):
            sub_df = df[df["月份"] == month]
            month_text = " ".join(sub_df["標題"].tolist())
            keywords = jieba.analyse.extract_tags(month_text, topK=5)
            st.markdown(f"**{month.strftime('%Y-%m')}：** {', '.join(keywords)}")
else:
    st.info("請上傳 Word 檔案以開始分析。")
