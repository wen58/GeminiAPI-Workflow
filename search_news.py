import os
import time
import urllib3
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 0. 基礎設定與環境初始化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_selenium_driver():
    """初始化並回傳一個 Headless Chrome Driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# ==========================================
# ==========================================
# 1. Google News RSS 爬蟲區塊
# ==========================================
def crawl_google_news_rss(keyword="台新 新光 合併"):
    print(f"\n--- [Section 2: Google News RSS - {keyword}] ---")
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    res = requests.get(rss_url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item')
        news_list = []
        for item in items[:5]:
            news_list.append({
                "標題": item.title.text,
                "發布時間": item.pubDate.text,
                "連結": item.link.text
            })
            print(f"找到新聞: {item.title.text}")
        return pd.DataFrame(news_list)
    else:
        print(f"❌ RSS 抓取失敗: {res.status_code}")
        return None

# ==========================================
# 2. 台新銀行特定公告爬蟲區塊
# ==========================================
def crawl_taishin_notice():
    print("\n--- [Section 3: 台新銀行重要公告] ---")
    url = "https://www.taishinbank.com.tw/TSB/personal/common/important-notice/TSBankImportantNotice-001358/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        container = soup.find('div', class_='editor-txt')
        if container:
            paragraphs = container.find_all('p')
            print("✅ 台新銀行公告內文抓取成功！")
            for p in paragraphs:
                print(p.text.strip())
        else:
            print("❌ 找不到 editor-txt 容器")
    except Exception as e:
        print(f"❌ 台新銀行爬取失敗: {e}")

# ==========================================
# 3. 台新金控重大訊息 (Selenium 雙層爬蟲)
# ==========================================
def crawl_taishin_holdings_news():
    print("\n--- [Section 4: 台新金控重大訊息抓取] ---")
    base_url = "https://www.tsholdings.com.tw"
    list_url = f"{base_url}/tsh/issue/issue3/"
    driver = get_selenium_driver()
    
    try:
        driver.get(list_url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('li', class_='m-li-cnt')
        
        final_data = []
        for li in items[:5]:
            update_time = li.find('time').text.strip() if li.find('time') else "未知時間"
            link_tag = li.find('a', class_='m-li-itm')
            if not link_tag: continue
            
            title = link_tag.text.strip()
            href = link_tag.get('href')
            full_url = base_url + href if href.startswith('/') else href
            
            print(f"🚀 正在進入詳細頁：{title}")
            driver.get(full_url)
            time.sleep(3)
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            container = detail_soup.find('div', class_='m-edt')
            
            content = "⚠️ 找不到 m-edt"
            if container:
                paragraphs = container.find_all('p')
                content = "\n".join([p.text.strip().replace('\xa0', ' ') for p in paragraphs if p.text.strip()])
            
            final_data.append({"更新時間": update_time, "標題": title, "作者": "wen58", "內容": content})
            
        df = pd.DataFrame(final_data)
        df.to_csv("taishin_news_wen58.csv", index=False, encoding="utf-8-sig")
        print("✨ 台新金控 CSV 已儲存。")
    finally:
        driver.quit()

# ==========================================
# 4. 中央社搜尋爬蟲 (Selenium 雙層爬蟲)
# ==========================================
def crawl_cna_news():
    print("\n--- [Section 5: 中央社新聞抓取] ---")
    search_url = "https://www.cna.com.tw/search/hysearchws.aspx?q=%E6%96%B0%E5%85%89%E4%BA%BA%E5%A3%BD"
    base_url = "https://www.cna.com.tw"
    driver = get_selenium_driver()
    
    try:
        driver.get(search_url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select("#jsMainList li")
        
        final_data = []
        for li in items[:5]:
            time_tag = li.select_one(".date")
            update_time = time_tag.text.strip() if time_tag else "未知時間"
            link_tag = li.select_one("a")
            if not link_tag: continue
            
            title = link_tag.select_one("h2").text.strip() if link_tag.select_one("h2") else link_tag.text.strip()
            href = link_tag.get('href', '')
            full_url = base_url + href if href.startswith('/') else href
            
            print(f"👉 處理中央社：{title}")
            driver.get(full_url)
            time.sleep(3)
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            container = detail_soup.select_one(".paragraph") or detail_soup.select_one(".centralContent")
            
            content = "⚠️ 找不到內容"
            if container:
                paragraphs = container.find_all('p')
                content = "\n".join([p.text.strip().replace('\xa0', ' ') for p in paragraphs if p.text.strip() and "（編輯：" not in p.text])
            
            final_data.append({"更新時間": update_time, "標題": title, "作者": "wen58", "內容": content})
            
        df = pd.DataFrame(final_data)
        df.to_csv("cna_news_wen58.csv", index=False, encoding="utf-8-sig")
        print("✨ 中央社 CSV 已儲存。")
    finally:
        driver.quit()

# ==========================================
# 主執行程式入口
# ==========================================
if __name__ == "__main__":
    # 執行你想要的區塊 (可以註解掉不需要的部分)
    # run_gemini_test()
    
    # df_rss = crawl_google_news_rss()
    
    # crawl_taishin_notice()
    
    crawl_taishin_holdings_news()
    
    crawl_cna_news()
    
    print("\n🏁 恭喜 wen58！所有選定任務執行完成。")