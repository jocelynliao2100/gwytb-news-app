import streamlit as st
from docx import Document
import pandas as pd
import jieba.analyse

st.set_page_config(page_title="國台辦新聞稿分析", layout="wide")
st.title("📑 國台辦新聞稿分析首頁")

# 側邊欄選單
menu = st.sidebar.radio("選擇頁面", [
    "五大欄目基本資訊",
    "關鍵字分析",
    "「交往交流」欄目分析"
])

# 處理 docx 檔案
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

uploaded_file = st.file_uploader("請上傳 Word 檔（例如：國台辦原始碼）", type="docx")

if uploaded_file:
    df = parse_docx(uploaded_file)

    if menu == "五大欄目基本資訊":
        st.subheader("🗂️ 基本資訊總覽")
        st.write(f"總共載入 {len(df)} 筆新聞資料")
        st.dataframe(df)

        with st.expander("📊 新聞發布數量（依日期統計）"):
            st.bar_chart(df["日期"].value_counts().sort_index())

    elif menu == "關鍵字分析":
        st.subheader("🔍 前 20 常見關鍵字")
        full_text = " ".join(df["標題"])
        top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
        st.dataframe(keyword_df)
        st.bar_chart(keyword_df.set_index("關鍵字"))

    elif menu == "「交往交流」欄目分析":
        st.subheader("🌐 分析『交往交流』欄目相關內容")
        filtered_df = df[df["標題"].str.contains("交流|交往|台胞|台青|座談|研習|文創|聯誼")]
        st.write(f"共篩選出 {len(filtered_df)} 筆相關新聞")
        st.dataframe(filtered_df)

        with st.expander("📆 日期統計圖"):
            st.bar_chart(filtered_df["日期"].value_counts().sort_index())

else:
    st.info("請先上傳檔案以啟用功能")
