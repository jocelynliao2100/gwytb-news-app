import streamlit as st
from five_column_view import render_five_column_analysis

# 設定首頁
st.set_page_config(page_title="國台辦新聞稿分析", layout="wide")
st.title("🇨🇳 國台辦新聞稿分析首頁")

# 左側選單
menu = st.sidebar.radio("📁 選擇分析模組", [
    "首頁",
    "五大欄目基本資訊",
    "關鍵字分析",
    "「交往交流」欄目分析"
])

# 首頁導覽說明
if menu == "首頁":
    st.markdown("""
    歡迎使用 **國台辦新聞稿分析系統**！📊

    本系統提供以下模組供互動分析使用：

    1. 📂 **五大欄目基本資訊**  
       分析五欄目新聞數量、時間分布與可視化呈現。

    2. 🔍 **標題關鍵字分析**  
       抽取新聞標題中的政治關鍵詞並視覺化，如「台獨」、「民進黨」、「賴清德」、「美國」等。

    3. 🌐 **「交往交流」欄目分析**  
       聚焦與「青年」、「台商」、特定中國地區有關的新聞交流內容與關鍵詞。

    👉 請從左側選單選擇你想使用的模組。
    """)

elif menu == "五大欄目基本資訊":
    render_five_column_analysis()

elif menu == "關鍵字分析":
    st.info("請使用左側選單進入「關鍵字分析」頁面（由 pages/keywords.py 自動掛載）")

elif menu == "「交往交流」欄目分析":
    st.info("請使用左側選單進入「交往交流欄目分析」頁面（由 pages/*.py 自動掛載）")
