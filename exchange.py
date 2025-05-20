import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from collections import defaultdict
from docx import Document

def render_exchange_analysis():
    uploaded_file = st.file_uploader("📂 請上傳交往交流原始 Word 檔案（含 HTML 結構）", type="docx")

    if uploaded_file:
        st.title("🌐 交往交流欄目分析")
        doc = Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        # 🔧 修正亂碼：清理 HTML 標籤、空白、只保留有日期或完整中文標題
        titles = []
        for line in paragraphs:
            clean_line = re.sub(r"<[^>]+>", "", line)  # 去除 HTML 標籤
            clean_line = clean_line.replace(" ", "").strip()  # 去除全形空格與空白
            if re.match(r"^\[\s?20\d{2}-\d{2}-\d{2}\s?\]", clean_line) or re.search(r"[\u4e00-\u9fff]{4,}", clean_line):
                if len(re.sub(r"[^\u4e00-\u9fff]", "", clean_line)) >= 4:
                    titles.append(clean_line)

        categories = {
            "青年交流": ["青年", "学生", "实习", "研学营", "交流月", "冬令营", "体育营", "职场", "青创", "打卡"],
            "文化宗教": ["文化", "祭祖", "诗词", "书画", "论语", "文昌", "大禹", "神农", "嫘祖", "黄帝", "汉服"],
            "節慶民俗": ["元宵", "春节", "年味", "中秋", "春茶", "三月三", "联谊", "灯火", "非遗"],
            "經貿產業": ["招商", "经贸", "产业", "合作", "金融", "链", "座谈", "营商", "发展"],
            "地方社區": ["参访", "慰问", "服务平台", "建桥", "条例", "法", "宣传", "普法", "连心"],
            "體育藝術": ["篮球", "街舞", "杂技", "书画", "艺术", "演出"]
        }

        def classify(title):
            for cat, kw_list in categories.items():
                if any(kw in title for kw in kw_list):
                    return cat
            return "未分類"

        stat = defaultdict(int)
        detail_rows = []
        for title in titles:
            cat = classify(title)
            stat[cat] += 1
            if cat != "未分類":
                detail_rows.append((cat, title))

        df_summary = pd.DataFrame(stat.items(), columns=["類別", "數量"]).sort_values("數量", ascending=False)
        df_detail = pd.DataFrame(detail_rows, columns=["分類", "標題"]).sort_values("分類")

        st.markdown("### 🎯 六類活動類別統計")
        st.dataframe(df_summary)

        st.markdown("### 📰 活動標題彙整（依分類）")
        for cat in df_detail["分類"].unique():
            with st.expander(f"{cat} 的活動標題"):
                for t in df_detail[df_detail["分類"] == cat]["標題"]:
                    st.markdown(f"- {t}")

        st.markdown("### 📍 中國地名熱點圖")

        # 🔍 此處省略的地圖資料與 Plotly 畫圖原樣保留（與你原始 code 相同）
        # 建議直接使用你提供的地名資料與畫圖邏輯，或我也可為你整合進來

        st.info("✅ 標題清理完畢，可避免亂碼或無效資料。")
    else:
        st.info("請上傳 Word 檔案進行分析。")
