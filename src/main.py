import os
import pandas as pd
from google import genai
from dotenv import load_dotenv

from search_news import crawl_taishin_holdings_news, crawl_cna_news
from api_connect import load_config, build_bulk_prompt, get_gemini_response
from make_html import md_to_ivory_html

if __name__ == "__main__":
    # 1. 環境設定
    load_dotenv(dotenv_path=".env.secret")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    config = load_config()

    # 2. 執行爬蟲 (從 searchtool 來的)
    crawl_taishin_holdings_news()
    crawl_cna_news()

    # 3. 整合數據
    dfs = [pd.read_csv(f, encoding="utf-8-sig") for f in ["doc/taishin_news_wen58.csv", "doc/cna_news_wen58.csv"] if os.path.exists(f)]
    
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

        # 4. AI 分析 (從 apitool 來的)
        print("\n--- [Gemini 分析中...] ---")
        prompt = build_bulk_prompt(combined_df.head(10), config)
        summary = get_gemini_response(client, prompt, config)
        
        with open("./doc/analysis_report.md", "w", encoding="utf-8") as f:
            f.write(f"# 台新新光集團合併新聞分析報告\n\n")
            f.write(f"分析時間：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(summary)

        # 5. 生成報告 (從 apitool 來的)
        md_to_ivory_html(md_file="./doc/analysis_report.md", html_file="./doc/analysis_report.html")
        print("\n🏁 全自動流程完成！請查看 analysis_report.html")