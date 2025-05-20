import streamlit as st
import pandas as pd
import jieba
import jieba.analyse
from docx import Document
from bs4 import BeautifulSoup
import re
from datetime import datetime
from collections import Counter

# 自訂關鍵字群組（美國與美方視為同義，統一統計）
KEYWORD_CATEGORIES = {
    "台獨相關": ["台獨", "民進黨", "賴清德", "蔡英文"],
    "國民黨相關": ["國民黨", "馬英九"],
    "美國相關": ["美國"],  # 統一為「美國」
    "經濟發展與交流相關": ["發展", "台商", "青年"],
    "其他": ["九二共識", "兩國論", "2758"]
}

# 所有關鍵字映射（統一同義詞）
KEYWORD_ALIAS = {
    "美國": ["美國", "美方"]
}

ALL_KEYWORDS = set()
for v in KEYWORD_CATEGORIES.values():
    ALL_KEYWORDS.update(v)
for v in KEYWORD_ALIAS.values():
    ALL_KEYWORDS.update(v)


def render_keywords_analysis():
    st.title("🔍 國台辦新聞內容關鍵字分析（HTML Word 檔）")

    uploaded_files = st.file_uploader(
        "📂 請上傳多個 HTML 原始碼格式的 Word 檔（.docx）",
        type="docx",
        accept_multiple_files=True
    )

    if uploaded_files:
        records = []

        for file in uploaded_files:
            doc = Document(file)
            html = "\n".join(p.text for p in doc.paragraphs)
            soup = BeautifulSoup(html, "html.parser")

            for li in soup.find_all("li"):
                date_tag = li.find("span")
                link_tag = li.find("a")
                if date_tag and link_tag:
                    date = date_tag.text.strip("[] ")
                    content = link_tag.get("title", "").strip()
                    if re.match(r"\d{4}-\d{2}-\d{2}", date) and content:
                        records.append({"日期": date, "內容": content})

        df = pd.DataFrame(records)
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        df = df.dropna(subset=["日期"])
        df["月份"] = df["日期"].dt.to_period("M").dt.to_timestamp()

        st.success(f"✅ 成功載入 {len(df)} 則新聞內容")
        st.dataframe(df)

        # 全文關鍵字統計
        st.markdown("### 🔠 所有新聞內容關鍵字（Top 20）")
        full_text = " ".join(df["內容"].tolist())
        top_keywords = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        keyword_df = pd.DataFrame(top_keywords, columns=["關鍵字", "權重"])
        st.bar_chart(keyword_df.set_index("關鍵字"))

        # 關鍵字群組分析（同義詞統一）
        st.markdown("### 📊 指定關鍵字群組出現趨勢分析")
        keyword_monthly = []
        for month, group in df.groupby("月份"):
            contents = " ".join(group["內容"].tolist())
            for label, words in KEYWORD_CATEGORIES.items():
                for word in words:
                    alias_list = KEYWORD_ALIAS.get(word, [word])
                    count = sum(contents.count(alias) for alias in alias_list)
                    keyword_monthly.append({"月份": month, "關鍵字": word, "出現次數": count})

        km_df = pd.DataFrame(keyword_monthly)

        for group_name, keywords in KEYWORD_CATEGORIES.items():
            st.subheader(f"📌 {group_name}")
            filtered = km_df[km_df["關鍵字"].isin(keywords)]
            pivot = filtered.pivot(index="月份", columns="關鍵字", values="出現次數").fillna(0)
            st.line_chart(pivot)

            for keyword in keywords:
                subset = km_df[km_df["關鍵字"] == keyword]
                top_months = subset.sort_values("出現次數", ascending=False).head(5)
                st.markdown(f"**🔍 {keyword}：出現次數最多的前五個月份：**")
                st.table(top_months[["月份", "出現次數"]])

                for _, row in top_months.iterrows():
                    m = row["月份"]
                    m_df = df[df["月份"] == m]
                    matched_contents = [t for t in m_df["內容"] if any(alias in t for alias in KEYWORD_ALIAS.get(keyword, [keyword]))]
                    with st.expander(f"📰 {m.strftime('%Y-%m')} 出現 {keyword} 的新聞內容（共 {len(matched_contents)} 筆）"):
                        for t in matched_contents:
                            st.markdown(f"- {t}")
    else:
        st.info("請上傳至少一個 Word 檔案以進行分析。")
