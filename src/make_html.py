import markdown
import os
import pandas as pd
import re

def md_to_ivory_html(md_file="analysis_report.md", html_file="analysis_report.html"):
    if not os.path.exists(md_file):
        print(f"❌ 找不到檔案：{md_file}")
        return

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 1. 物理清洗：去掉所有 * 和 ** (文千要求的去星號) ---
    content = content.replace("**", "")
    content = re.sub(r'(?m)^\s*\*+\s*', '', content)

    # --- 2. 轉換 HTML (nl2br 確保原始換行) ---
    html_body = markdown.markdown(content, extensions=['extra', 'nl2br'])

    # --- 🌟 3. 更新後的質感配色方案（附圖風格） ---
    css_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Noto+Serif+TC:wght@700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

        :root {
            --page-bg: #eae2d8;        /* 暖灰色頁面背景 (Greige/Sand) - 復刻附圖外部背景 */
            --card-bg: #ffffff;        /* 純白色卡片背景 - 復刻附圖卡片主體 */
            --text-dark: #374151;      /* 深石墨色 - 主體與強調文字 */
            --text-muted: #9ca3af;     /* 淡灰色 - 頁腳與淡線條 */
        }

        body {
            font-family: 'Inter', 'Noto Sans TC', sans-serif;
            background-color: var(--page-bg); /* 暖灰色頁面背景 */
            color: var(--text-dark);
            line-height: 1.8;
            margin: 0;
            padding: 80px 20px;
            letter-spacing: 0.02em;
        }

        .report-paper {
            max-width: 850px;
            margin: 0 auto;
            background-color: var(--card-bg); /* 純白色卡片背景 */
            padding: 60px 80px; /* 調整留白比例，更現代高質感 */
            border-radius: 4px; /* 添加微小圓角 */
            /* 移除明顯的卡片陰影，改用淡淡的現代陰影區隔 */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
            position: relative;
        }

        h1 {
            font-family: 'Noto Serif TC', serif;
            color: var(--text-dark);
            font-size: 2.5em;
            margin-bottom: 40px;
            text-align: left;
        }

        /* 換行照舊，不加符號 */
        p {
            margin-bottom: 1.5em;
            white-space: pre-wrap;
            font-weight: 300;
        }

        /* 現代專業報表的區隔感，移除金色側邊框 */
        h2 {
            font-family: 'Noto Serif TC', serif;
            color: var(--text-dark);
            font-size: 1.5em;
            margin-top: 60px;
            margin-bottom: 20px;
            border-left: none; /* 徹底移除金色側邊框 */
            padding-left: 0;
        }

        .footer {
            margin-top: 100px;
            font-size: 0.85em;
            color: var(--text-muted); /* 改為淡灰色 */
            text-transform: uppercase;
            letter-spacing: 0.2em;
            text-align: left;
            border-top: 1px solid var(--text-muted); /* 將分隔線顏色也改為淡灰色 */
            padding-top: 20px;
        }

        /* 移除加粗後的過度黑度，維持石墨色 */
        b, strong {
            color: var(--text-dark);
            font-weight: 600;
        }
    </style>
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <title>Intelligence Briefing | wen58</title>
        {css_style}
    </head>
    <body>
        <div class="report-paper">
            {html_body}
            <div class="footer">
                Wen58 Intelligence System • {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✨ 質感色彩升級版 HTML 已生成：{html_file}")

if __name__ == "__main__":
    md_to_ivory_html()