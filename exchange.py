# 安裝必要套件
!pip install python-docx

from docx import Document
from google.colab import files
import re
from collections import defaultdict
from io import BytesIO
import pandas as pd

# 上傳 Word 檔
uploaded = files.upload()
for filename in uploaded.keys():
    doc = Document(BytesIO(uploaded[filename]))

# 擷取所有段落文字
all_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
titles = [line for line in all_text if re.match(r'^\[ ?20\d{2}-\d{2}-\d{2} ?\]', line) or re.search(r'[\u4e00-\u9fff]{4,}', line)]

# 活動分類定義（六類）
categories = {
    "青年交流": ["青年", "學生", "實習", "研學營", "交流月", "冬令營", "體育營", "職場", "青創", "打卡"],
    "文化宗教": ["文化", "祭祖", "詩詞", "書畫", "論語", "文昌", "大禹", "神農", "嫘祖", "黃帝", "漢服"],
    "節慶民俗": ["元宵", "春節", "年味", "中秋", "春茶", "三月三", "聯誼", "燈火", "非遺"],
    "經貿產業": ["招商", "經貿", "產業", "合作", "金融", "鏈", "座談", "營商", "發展"],
    "地方社區": ["參訪", "慰問", "服務平台", "建橋", "條例", "法", "宣傳", "普法", "連心"],
    "體育藝術": ["籃球", "街舞", "雜技", "書畫", "藝術", "演出"]
}

# 活動分類函式
def classify(title):
    for cat, keywords in categories.items():
        if any(kw in title for kw in keywords):
            return cat
    return "未分類"

# 統計分類 + 儲存每筆分類標題
stat = defaultdict(int)
classified_titles = []
detailed_titles = []  # 專門記錄非未分類的具體標題

for title in titles:
    cat = classify(title)
    stat[cat] += 1
    classified_titles.append((title, cat))
    if cat != "未分類":
        detailed_titles.append((cat, title))

# 顯示分類統計
df_summary = pd.DataFrame(list(stat.items()), columns=["類別", "數量"]).sort_values(by="數量", ascending=False)
from IPython.display import display
display(df_summary)

# 顯示六類活動具體標題
df_detail = pd.DataFrame(detailed_titles, columns=["分類", "標題"]).sort_values(by="分類")
display(df_detail)

# 匯出 CSV 檔案
df_detail.to_csv("交流交往_六類活動標題.csv", index=False)
files.download("交流交往_六類活動標題.csv")

