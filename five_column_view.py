import streamlit as st
from docx import Document
from bs4 import BeautifulSoup
import pandas as pd
import re

def render_five_column_analysis():
    st.subheader("📂 五大欄目基本資訊（多檔分析）")

    uploaded_files = st.file_uploader(
        "請上傳多個國台辦 Word 檔案（HTML 原始碼形式）",
        type="docx",
        accept_multiple_files=True
    )

    def extract_news_from_docx(file):
        doc = Document(file)
        html = "\n".join(p.text for p in doc.paragraphs)
        soup = BeautifulSoup(html, "html.parser")

        column_meta = soup.find("meta", attrs={"name": "ColumnName"})
        column_name = column_meta["content"] if column_meta else "未知欄目"

        news_items = []
        for li in soup.find_all("li"):
            date_tag = li.find("span")
            link_tag = li.find("a")
            if date_tag and link_tag:
                date = date_tag.text.strip("[] ")
                title = link_tag.get("title", "").strip()
                if re.match(r"\d{4}-\d{2}-\d{2}", date) and title:
                    news_items.append({
                        "日期": date,
                        "標題": title,
                        "欄目": column_name
                    })
        return news_items

    if uploaded_files:
        all_data = []
        for f in uploaded_files:
            all_data.extend(extract_news_from_docx(f))

        df = pd.DataFrame(all_data)
        st.success(f"✅ 共解析出 {len(df)} 則新聞，涵蓋 {df['欄目'].nunique()} 個欄目")
        st.dataframe(df)

        st.markdown("### 🧭 各欄目新聞數量")
        st.bar_chart(df["欄目"].value_counts())

        st.markdown("### 📅 各欄目按日期分布")
        pivot = df.groupby(["欄目", "日期"]).size().reset_index(name="數量")
        pivot_wide = pivot.pivot(index="日期", columns="欄目", values="數量").fillna(0)
        st.line_chart(pivot_wide)

    else:
        st.info("請上傳至少一個 .docx 檔案以進行分析")
