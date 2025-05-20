import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
import datetime
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
        titles_with_date = []  # 用於儲存帶有日期的標題
        
        for line in paragraphs:
            clean_line = re.sub(r"<[^>]+>", "", line)  # 去除 HTML 標籤
            clean_line = clean_line.replace(" ", "").strip()  # 去除全形空格與空白
            
            # 提取日期和標題
            date_match = re.search(r"\[\s?(20\d{2}-\d{2}-\d{2})\s?\]", clean_line)
            if date_match:
                date_str = date_match.group(1)
                title_text = re.sub(r"\[\s?20\d{2}-\d{2}-\d{2}\s?\]", "", clean_line).strip()
                if len(re.sub(r"[^\u4e00-\u9fff]", "", title_text)) >= 4:
                    titles.append(clean_line)
                    titles_with_date.append((date_str, title_text))
            elif re.search(r"[\u4e00-\u9fff]{4,}", clean_line):
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
        
        # 處理帶有日期的標題，用於繪製時間趨勢圖
        date_category_data = []
        
        for date_str, title_text in titles_with_date:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                # 將日期轉換為年月格式
                year_month = date_obj.strftime("%Y-%m")
                
                # 分類該標題
                category = classify(title_text)
                
                # 儲存日期、類別和標題
                if category != "未分類":
                    date_category_data.append((year_month, category, title_text))
            except ValueError:
                # 如果日期格式不正確，則跳過
                continue
                
        # 建立時間趨勢數據
        time_trend_data = defaultdict(lambda: defaultdict(int))
        
        for year_month, category, _ in date_category_data:
            time_trend_data[year_month][category] += 1
            
        # 轉換為DataFrame，用於繪製圖表
        time_trend_rows = []
        
        for year_month, categories in time_trend_data.items():
            for category, count in categories.items():
                time_trend_rows.append({
                    "年月": year_month,
                    "類別": category,
                    "數量": count
                })
                
        if time_trend_rows:
            df_time_trend = pd.DataFrame(time_trend_rows)
            
            # 確保日期排序正確
            df_time_trend["年月"] = pd.to_datetime(df_time_trend["年月"])
            df_time_trend = df_time_trend.sort_values("年月")
            df_time_trend["年月"] = df_time_trend["年月"].dt.strftime("%Y-%m")
            
            # 透過樞紐表將資料轉換為適合繪製折線圖的格式
            pivot_df = pd.pivot_table(
                df_time_trend,
                index="年月", 
                columns="類別", 
                values="數量", 
                fill_value=0
            ).reset_index()
            
            # 繪製時間趨勢折線圖
            st.markdown("### 📈 六類活動時間趨勢")
            
            fig_trend = go.Figure()
            
            for category in pivot_df.columns[1:]:  # 第一列是年月，從第二列開始是各類別
                fig_trend.add_trace(go.Scatter(
                    x=pivot_df["年月"],
                    y=pivot_df[category],
                    mode="lines+markers",
                    name=category,
                    connectgaps=True
                ))
                
            fig_trend.update_layout(
                title="六類活動隨時間變化",
                xaxis_title="年月",
                yaxis_title="活動數量",
                legend_title="活動類別",
                height=500
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("### 📰 活動標題彙整（依分類）")
        for cat in df_detail["分類"].unique():
            with st.expander(f"{cat} 的活動標題"):
                for t in df_detail[df_detail["分類"] == cat]["標題"]:
                    st.markdown(f"- {t}")
        
        data = {
            "地点": [
                "贵州", "成都", "四川", "武汉", "重庆", "广东", "福建", "珠海", "广州", "青岛", "南京", "东莞",
                "山东", "湖北", "江西", "广西", "北京", "河南", "济南", "新疆", "汕尾", "杭州", "江苏", "浙江",
                "上海", "沈阳", "厦门", "汕头", "福州", "大连", "合肥", "安徽", "绵阳", "深圳", "湛江", "昆山",
                "佛山", "黑龙江", "河北", "潮州", "苏州", "贵阳", "郑州", "香港", "甘肃", "梅州", "惠州", "温州",
                "南宁", "哈尔滨", "陕西", "洛阳", "南沙", "平潭", "漳州", "海南", "西湖", "潮汕", "南昌"
            ],
            "次数": [
                289, 260, 232, 226, 225, 202, 174, 160, 157, 155, 133, 132,
                123, 109, 108, 108, 105, 97, 90, 89, 87, 85, 84, 75,
                68, 67, 57, 57, 57, 48, 47, 45, 43, 40, 40, 40,
                38, 36, 35, 33, 33, 32, 32, 31, 31, 30, 25, 24,
                21, 21, 21, 19, 19, 19, 19, 19, 18, 17, 16
            ]
        }
        
        location_data = {
            "贵州": (106.8748, 26.8154), "成都": (104.0665, 30.5726), "四川": (102.7098, 30.6171),
            "武汉": (114.2986, 30.5844), "重庆": (106.5516, 29.5630), "广东": (113.2644, 23.1291),
            "福建": (119.2965, 26.0745), "珠海": (113.5767, 22.2707), "广州": (113.2644, 23.1291),
            "青岛": (120.3826, 36.0671), "南京": (118.7969, 32.0617), "东莞": (113.7518, 23.0207),
            "山东": (117.0204, 36.6683), "湖北": (114.3419, 30.5467), "江西": (115.8582, 28.6832),
            "广西": (108.3275, 22.8150), "北京": (116.4074, 39.9042), "河南": (113.6654, 34.7570),
            "济南": (117.1200, 36.6512), "新疆": (87.6168, 43.8256), "汕尾": (115.3753, 22.7862),
            "杭州": (120.1551, 30.2741), "江苏": (118.7632, 32.0617), "浙江": (120.1536, 30.2656),
            "上海": (121.4737, 31.2304), "沈阳": (123.4315, 41.8057), "厦门": (118.0895, 24.4798),
            "汕头": (116.6822, 23.3535), "福州": (119.2965, 26.0745), "大连": (121.6147, 38.9140),
            "合肥": (117.2272, 31.8206), "安徽": (117.2849, 31.8616), "绵阳": (104.6796, 31.4675),
            "深圳": (114.0579, 22.5431), "湛江": (110.3589, 21.2713), "昆山": (120.9807, 31.3856),
            "佛山": (113.1214, 23.0215), "黑龙江": (126.6424, 45.7560), "河北": (114.5025, 38.0455),
            "潮州": (116.6323, 23.6618), "苏州": (120.5853, 31.2983), "贵阳": (106.6302, 26.6477),
            "郑州": (113.6254, 34.7466), "香港": (114.1694, 22.3193), "甘肃": (103.8264, 36.0594),
            "梅州": (116.1176, 24.2991), "惠州": (114.4168, 23.1115), "温州": (120.6994, 27.9938),
            "南宁": (108.3669, 22.8170), "哈尔滨": (126.5349, 45.8038), "陕西": (108.9542, 34.2655),
            "洛阳": (112.4536, 34.6197), "南沙": (113.5958, 22.7855), "平潭": (119.7912, 25.5035),
            "漳州": (117.6536, 24.5130), "海南": (110.3486, 20.0174), "西湖": (120.1410, 30.2400),
            "潮汕": (116.6822, 23.3535), "南昌": (115.8582, 28.6832)
        }
        
        df_map = pd.DataFrame(data)
        df_map["lon"] = df_map["地点"].map(lambda x: location_data.get(x, (None, None))[0])
        df_map["lat"] = df_map["地点"].map(lambda x: location_data.get(x, (None, None))[1])
        df_map = df_map.dropna()
        
        fig = go.Figure(data=go.Scattergeo(
            lon=df_map['lon'],
            lat=df_map['lat'],
            text=df_map['地点'] + ": " + df_map['次数'].astype(str) + " 次",
            mode='markers',
            marker=dict(
                size=df_map['次数'] / 10,
                color=df_map['次数'],
                colorscale='Reds',
                opacity=0.8,
                colorbar=dict(title="出現次數")
            ),
        ))
        
        fig.update_layout(
            title_text='中國新聞地名熱點圖',
            geo=dict(
                scope='asia',
                showland=True,
                landcolor="LightGreen",
                showocean=True,
                oceancolor="LightBlue",
                projection_type='natural earth'
            ),
            height=700
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("請上傳 Word 檔案進行分析。")
