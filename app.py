import streamlit as st
from docx import Document
import pandas as pd
import jieba.analyse

st.set_page_config(page_title="國台辦新聞稿分析", layout="wide")

st.title("🇨🇳 國台辦新聞稿分析首頁")

st.markdown("""
歡迎使用 **國台辦新聞稿分析系統**！

請先在左側選單中選擇你要分析的功能，並上傳對應的 Word 檔案（.docx）。

本系統提供以下三個分析模組：

1. 📂 **五大欄目基本資訊**：分析新聞數量、時間分布與表格呈現  
2. 🔍 **關鍵字分析**：抽取新聞標題中的高頻關鍵詞並視覺化  
3. 🌐 **「交往交流」欄目分析**：聚焦與「青年」、「台胞」有關的欄目新聞

---

""")

# 側邊欄選單
menu = st.sidebar.radio("📁 選擇分析模組", [
    "首頁",
    "五大欄目基本資訊",
    "關鍵字分析",
    "「交往交流」欄目分析"
])

# 共用的檔案處理函式
def parse_docx(file):
    doc = Document(file)
    data = []
    for para in doc.paragraphs:
        line = para.text.strip()
        if line.startswith("[") and "]" in line:
            date = line.split("]")[0].strip("[]")
            title = line.split("]")[-1].strip()
            if title:
                data.append({"日期": date, "標題": title})
    return pd.DataFrame(data)

# 僅非首頁時顯示上傳
if menu != "首頁":
    uploaded_file = st.file_uploader("請上傳 Word 檔（例如：國台辦原始碼）", type="docx")

    if uploaded_file:
        df = parse_docx(uploaded_file)

        if menu == "五大欄目基本資訊":
            st.subheader("📂 五大欄目基本資訊")
            st.write(f"共載入 {len(df)} 筆新聞")
            st.dataframe(df)
            with st.expander("📊 日期分布圖"):
                st.bar_chart(df["日期"].value_counts().sort_index())

        elif menu == "關鍵字分析":
            st.subheader("🔍 關鍵字分析")
            full_text = " ".join(df["標題"])
            top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
            keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
            st.dataframe(keyword_df)
            st.bar_chart(keyword_df.set_index("關鍵字"))

        elif menu == "「交往交流」欄目分析":
            st.subheader("🌐 「交往交流」欄目分析")
            filtered_df = df[df["標題"].str.contains("交流|交往|台胞|台青|座談|研習|文創|聯誼")]
            st.write(f"共找到 {len(filtered_df)} 筆相關新聞")
            st.dataframe(filtered_df)
            with st.expander("📆 日期統計圖"):
                st.bar_chart(filtered_df["日期"].value_counts().sort_index())
    else:
        st.info("請先上傳檔案以啟用此功能")


