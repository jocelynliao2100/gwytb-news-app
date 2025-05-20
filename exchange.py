import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt
import matplotlib.pyplot as plt
import re
from collections import defaultdict
from docx import Document
from io import BytesIO
from datetime import datetime

def render_exchange_analysis():
    st.set_page_config(page_title="交往交流分析", layout="wide")
    st.title("🌐 交往交流欄目分析")

    uploaded_file = st.file_uploader("📂 請上傳交往交流原始 Word 檔案（含 HTML 結構）", type="docx")

    if uploaded_file:
        doc = Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        titles = [line for line in paragraphs if re.match(r"^\[ ?20\d{2}-\d{2}-\d{2} ?\]", line) or re.search(r"[\u4e00-\u9fff]{4,}", line)]

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

        st.markdown("### 📍 前 20 中國地名熱點圖")
        location_data = {
            "貴州": (106.8748, 26.8154), "成都": (104.0665, 30.5726), "重慶": (106.5516, 29.5630), "廈門": (118.0895, 24.4798),
            "泉州": (118.6824, 24.8799), "福州": (119.2965, 26.0745), "武漢": (114.2986, 30.5844), "深圳": (114.0579, 22.5431),
            "廣州": (113.2644, 23.1291), "珠海": (113.5767, 22.2707), "東莞": (113.7518, 23.0207), "上海": (121.4737, 31.2304),
            "北京": (116.4074, 39.9042), "南京": (118.7969, 32.0617), "杭州": (120.1551, 30.2741), "台商": (114.0, 23.0)
        }

        all_text = " ".join(titles)
        city_counter = {city: all_text.count(city) for city in location_data.keys() if all_text.count(city) > 0}
        top_cities = sorted(city_counter.items(), key=lambda x: x[1], reverse=True)[:20]
        df_map = pd.DataFrame(top_cities, columns=["地名", "出現次數"])
        df_map["lon"] = df_map["地名"].map(lambda x: location_data[x][0])
        df_map["lat"] = df_map["地名"].map(lambda x: location_data[x][1])

        fig = go.Figure(data=go.Scattergeo(
            lon=df_map['lon'],
            lat=df_map['lat'],
            text=df_map['地名'] + ": " + df_map['出現次數'].astype(str) + " 次",
            mode='markers',
            marker=dict(
                size=df_map['出現次數'] / 5,
                color=df_map['出現次數'],
                colorscale='Reds',
                opacity=0.8,
                colorbar=dict(title="次數")
            ),
        ))

        fig.update_layout(
            title_text='交往交流新聞：中國地名熱點圖',
            geo=dict(scope='asia', showland=True, landcolor="LightGreen", showocean=True, oceancolor="LightBlue"),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("請上傳 Word 檔案進行分析。")
