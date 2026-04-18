```markdown
# 🏛️ Wen58 News Intelligence System

這是一個專為金融資訊愛好者設計的自動化新聞分析系統。它能從多個來源（如台新官網、中央社）抓取資訊，利用 **Gemini 2.5 Flash** 進行跨篇章的深度摘要，最後產出一份 HTML 分析報告。

## 🌟 核心功能

- **多源數據整合**：自動合併爬蟲檔案。
- **批量提詞工程 (Bulk Prompting)**：一次處理 5-10 篇新聞，節省 API 額度並進行跨篇章對比。
- **安全性設計**：金鑰與程式碼分離，透過 `.env.secret` 嚴密保護 API Key。


## 📁 檔案結構

```text
.
├── .env.secret.example      # 存放 GEMINI_API_KEY (不進版本控制)
├── prompt.yaml              # AI 指令、模型參數與提詞範本
├── main.py                  # 主執行程式：抓取、合併、呼叫 API
├── make_html.py             # 轉檔程式：Markdown 轉高質感 HTML
├── taishin_news_wen58.csv   # 台新官網爬蟲結果
├── cna_news_wen58.csv       # 中央社新聞爬蟲結果
├── analysis_report.md       # AI 生成的原始分析文件
├── analysis_report.html     # 最終生成的視覺化報告
└── requirements.txt         # 專案套件清單
```

### 1. 環境準備
確保你的電腦已安裝 Python 3.10+，並建議使用虛擬環境：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 設定金鑰
在專案目錄建立 `.env.secret.example`，並寫入個人.env.secret 並寫入 Google AI API Key：
```text
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### 3. 配置指令
編輯 `prompt.yaml` 來調整 AI 的分析語氣或角色設定。

### 4. 執行分析
```bash
python3 main.py
```

## 🛠️ 開發套件

- `google-genai`：Gemini 2.5 模型對接
- `pandas`：高效能數據合併與處理
- `python-dotenv`：安全環境變數讀取
- `markdown`：分析報告格式轉換

---
**Prepared by Wen-Chien Shih (Wen58)** *Data Scientist / Statistician based in Taipei*
```