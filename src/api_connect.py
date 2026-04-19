import pandas as pd
import yaml
import os
from google import genai
from dotenv import load_dotenv

# 1. 讀取 YAML (維持原樣)
def load_config(yaml_path="src/config/prompt.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 2. 製作「批量」Prompt (維持原樣，傳入合併後的 df)
def build_bulk_prompt(rows_df, config):
    articles_text = ""
    for i, (_, row) in enumerate(rows_df.iterrows()):
        # 加入來源標記，讓 AI 知道這是哪裡抓的
        source = "台新官網" if "taishin" in str(row.get('來源', '')) else "中央社"
        
        articles_text += f"### 新聞條目 {i+1} [來源：{source}]\n"
        articles_text += f"【標題】：{row.get('標題', '無標題')}\n"
        articles_text += f"【時間】：{row.get('更新時間', '無時間')}\n"
        articles_text += f"【內容】：{str(row.get('內容', ''))[:800]}...\n\n"

    template = config['news_analysis']['prompt_template']
    full_prompt = template.format(merged_contents=articles_text)
    return full_prompt

# 3. 取得 API 回應
def get_gemini_response(client, prompt, config):
    try:
        response = client.models.generate_content(
            model=config['gemini_config']['model'],
            contents=prompt,
            config={
                "system_instruction": config['gemini_config']['system_instruction']
            }
        )
        return response.text
    except Exception as e:
        return f"❌ API 請求失敗: {e}"

# ==========================================
# 🏁 主執行區塊：雙來源合併
# ==========================================
if __name__ == "__main__":
    load_dotenv(dotenv_path=".env.secret")
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)
    config = load_config("src/config/prompt.yaml")
    
    file_list = ["taishin_news_wen58.csv", "cna_news_wen58.csv"]
    all_dfs = []

    # --- 步驟 A: 遍歷讀取所有 CSV ---
    data_folder = "doc" 

    for file in file_list:
        # 🌟 使用 os.path.join 組合路徑，變成 doc/taishin_news_wen58.csv
        file_path = os.path.join(data_folder, file)
        
        if os.path.exists(file_path):
            # 🌟 讀取時使用組合好的完整路徑
            temp_df = pd.read_csv(file_path, encoding="utf-8-sig")
            
            # 增加一個來源標籤，方便 AI 辨識
            temp_df['來源'] = file
            all_dfs.append(temp_df)
            print(f"✅ 已從 {data_folder} 載入：{file} ({len(temp_df)} 筆)")
        else:
            print(f"⚠️ 找不到檔案：{file_path}，請檢查 doc 資料夾內容")

    # --- 步驟 B: 合併資料 ---
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        # 為了節省額度，我們取合併後的「前 10 筆」進行綜合分析
        target_df = combined_df.head(10) 
        
        print(f"🚀 正在打包來自不同來源的 {len(target_df)} 篇新聞送往 Gemini...")

        # --- 步驟 C: 組合與分析 ---
        bulk_prompt = build_bulk_prompt(target_df, config)
        
        # 🌟 正式執行時把下面註解拿掉
        final_summary = get_gemini_response(client, bulk_prompt, config)
        
        print("\n" + "★"*20)
        print("🤖 Gemini 綜合分析報告：")
        print(final_summary)
        print("★"*20)

        # --- 步驟 D: 儲存報告 ---
        with open("doc/analysis_report.md", "w", encoding="utf-8") as f:
            f.write(f"# 台新新光集團合併新聞分析報告\n\n")
            f.write(f"分析時間：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(final_summary)
            
        print(f"\n💾 報告已儲存：doc/analysis_report.md")
    else:
        print("❌ 沒有任何 CSV 檔案可供分析。")