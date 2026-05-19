# InsightBooks-NLP-Book-Review-Analyzer

# 博客來評論分析 NLP 系統

本專案以 **自然語言處理（NLP）** 技術分析博客來書籍評論，協助使用者快速理解書籍評價特徵，並提供更具參考價值的閱讀分析結果。

系統整合 **評論爬蟲、文字前處理、情緒分析、評論分類、自動摘要、關鍵字分析、文字雲視覺化與互動式評論探索功能**，並透過 Flask 建立 Web 儀表板提供互動分析。


---

## 功能特色

- ✅ 博客來評論爬蟲
- ✅ 前處理 / 中文分詞 / 詞性標註
- ✅ Azure 情緒分析
- ✅ 評論分類分析
- ✅ 自動摘要（好評 / 普通評論 / 負評）
- ✅ 關鍵字分析
- ✅ 文字雲視覺化
- ✅ 評論探索互動
- ✅ NLP Pipeline 檢視頁面
- ✅ 預設書籍分析

---

## 系統流程

```text
博客來評論
    ↓
評論爬蟲
    ↓
資料前處理
(清理 / 分詞 / 詞性標註)
    ↓
 ┌────────────┬────────────┬────────────┬────────────┐
 ↓            ↓            ↓            ↓

情緒分析   評論分類     自動摘要     關鍵字分析

 ↓            ↓            ↓            ↓

Pie Chart   分類圖表    評論摘要     文字雲
```

---

## 系統展示

### 首頁

系統首頁整合：

- 情緒分析
- 關鍵字分析
- 評論探索
- 評論分類分析
- 評論摘要

首頁分析介面：

![首頁1](webpic/首頁4.png)
![首頁2](webpic/首頁5.png)
![首頁3](webpic/首頁6.png)

---

### 評論探索功能

使用者可選擇評論進行互動分析：

功能：

- 顯示完整評論
- 情緒分析同步高亮
- 評論分類同步高亮

流程：

```text
評論探索
    ↓

選擇評論
    ↓

情緒分析同步
    ↓

評論分類同步
```

---

### NLP Pipeline

評論前處理與分頁展示：

![分頁1](webpic/分頁3.png)
![分頁2](webpic/分頁4.png)
---

## 專案結構

```text
博客來評論分析NLP2/

app.py

templates/
│
├── index.html
├── pipeline.html
│
└── components/
    ├── navbar.html
    ├── hero.html
    ├── search_card.html
    ├── emotion_card.html
    ├── keyword_card.html
    ├── explorer_card.html
    ├── classification_card.html
    └── summary_card.html

static/
│
├── css/
│   ├── style.css
│   └── pipeline.css
│
├── js/
│   └── main.js
│
└── images/
    └── hero-book.png

data/

input_crawler.py
preprocessing.py
sentiment_analysis.py
keyword_extraction2.py
text_classification.py
summarization.py

│── requirements.txt
│── .env
│── README.md
```

---

## 使用技術

### 後端

- Flask
- Pandas
- Requests
- BeautifulSoup4

### NLP

- Jieba
- NLTK
- SnowNLP
- Azure AI Text Analytics

功能：

- 情緒分析
- 評論分類
- 摘要生成
- 關鍵字萃取

### Frontend

- HTML
- Bootstrap 5
- Chart.js
- JavaScript

### 視覺化

- WordCloud
- Matplotlib

### 爬蟲

- Selenium
- webdriver-manager
- undetected-chromedriver

---

## 安裝方式

建立虛擬環境：

```bash
python -m venv venv
```

啟動虛擬環境：

Windows：

```bash
venv\Scripts\activate
```

安裝套件：

```bash
pip install -r requirements.txt
```

---

## 環境變數設定

建立 `.env`

```env
AZURE_LANGUAGE_ENDPOINT=YOUR_ENDPOINT
AZURE_LANGUAGE_KEY=YOUR_KEY
```


---

## 執行方式

啟動 Flask：

```bash
python app.py
```

開啟：

```text
http://127.0.0.1:5000
```

---

## 預設分析書籍

系統目前提供：

- 原子習慣
- 牧羊少年奇幻之旅
- 解憂雜貨店
- 被討厭的勇氣
- 底層邏輯：看清這個世界的底牌

---

## 分析結果

### 😊 情緒分析

輸出：

- Positive
- Neutral
- Negative

並提供：

- 評論數量
- 百分比統計
- Pie Chart 視覺化

---

### 📊 評論分類分析

分類：

- 內容品質分析
- 翻譯品質分析
- 實用性評估
- 閱讀體驗分析
- 價格與CP值分析
- 內容品質分析
- 其他

提供互動式分類圖表。

---

### 📝 評論摘要

依評分區分：

- 好評（4★以上）
- 普通評論（3★）
- 負評（1–2★）

---

### ☁ 關鍵字分析

輸出：

- Top Keywords
- 中文文字雲

---
