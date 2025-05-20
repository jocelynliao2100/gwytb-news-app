import streamlit as st
from docx import Document
import pandas as pd
import jieba.analyse
from bs4 import BeautifulSoup
import re
from five_column_view import render_five_column_analysis  # ✅ 匯入模組函式

# 設定頁面
st.set_page_config(page_title="國台辦新聞稿分析", layout="wide")
st.title("🇨🇳 國台辦新聞稿分析首頁")

# 主頁導覽說明
st.markdown("""
歡迎使用 **國台辦新聞稿分析系統**！

請先在左側選單中選擇你要分析的功能，並上傳對應的 Word 檔案（.docx）或 CSV 資料。

本系統提供以下三個分析模組：

1. 📂 **五大欄目基本資訊**：分析五欄目新聞數量、時間分布與視覺化呈現  
2. 🔍 **關鍵字分析**：抽取新聞標題中的政治關鍵詞並視覺化，如台獨、民進黨、賴清德和美國等  
3. 🌐 **「交往交流」欄目分析**：聚焦與「青年」、「台商」以及中國地點有關的關鍵字與新聞內容
---
""")

# 側邊欄選單
menu = st.sidebar.radio("📁 選擇分析模組", [
    "首頁",
    "五大欄目基本資訊",
    "關鍵字分析",
    "「交往交流」欄目分析"
])

# =============================
# 分析模組邏輯區段
# =============================

if menu == "五大欄目基本資訊":
    render_five_column_analysis()

elif menu == "關鍵字分析":
    st.subheader("🔍 關鍵字分析")
    uploaded_file = st.file_uploader("請上傳單一 Word 檔案（含標題）", type="docx")
    if uploaded_file:
        doc = Document(uploaded_file)
        titles = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = " ".join(titles)
        top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
        st.dataframe(keyword_df)
        st.bar_chart(keyword_df.set_index("關鍵字"))
    else:
        st.info("請先上傳含標題的 Word 檔")

elif menu == "「交往交流」欄目分析":
    st.subheader("🌐 『交往交流』欄目分析")
    uploaded_file = st.file_uploader("請上傳 Word 檔案（含標題與日期）", type="docx")
    if uploaded_file:
        doc = Document(uploaded_file)
        data = []
        for para in doc.paragraphs:
            line = para.text.strip()
            if line.startswith("[") and "]" in line:
                date = line.split("]")[0].strip("[]")
                title = line.split("]")[-1].strip()
                if any(kw in title for kw in ["交流", "交往", "台胞", "台青", "聯誼", "文創", "座談"]):
                    data.append({"日期": date, "標題": title})
        df = pd.DataFrame(data)
        st.write(f"共找到 {len(df)} 則相關新聞")
        st.dataframe(df)
        if not df.empty:
            st.bar_chart(df["日期"].value_counts().sort_index())
    else:
        st.info("請先上傳檔案以啟用此功能")
