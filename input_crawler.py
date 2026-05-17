import time
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import re

def extract_book_id(url):

    match = re.search(

        r'/products/(\d+)',

        url
    )

    if match:

        return match.group(1)

    return None

def crawl_book_reviews(book_id, book_name=None, max_pages=5):
    reviews_data = []
    os.makedirs('data', exist_ok=True)
    
    # --- 第一階段：Selenium 獲取 Cookie ---
    options = uc.ChromeOptions()
    print(f"🚀 啟動瀏覽器獲取權限 (ID: {book_id})...")
    driver = uc.Chrome(options=options, version_main=147)
    
    try:
        product_url = f"https://www.books.com.tw/products/{book_id}"
        driver.get(product_url)
        print("💡 請確認瀏覽器已載入頁面（若有驗證碼請手動點擊）...")
        time.sleep(10) 
        
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
            
        ua = driver.execute_script("return navigator.userAgent;")
        driver.quit()
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        try: driver.quit()
        except: pass
        return

    # --- 第二階段：POST 請求 (精準對位 htmlData) ---
    api_url = "https://www.books.com.tw/booksComment/ajaxCommemtFilter"
    headers = {
        "User-Agent": ua,
        "Referer": f"https://www.books.com.tw/booksComment/getCommemt/{book_id}",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.books.com.tw"
    }

    for page in range(1, max_pages + 1):
        print(f"🔍 正在抓取第 {page} 頁...")
        
        payload = {
            "type": "getCommemt",
            "stars[]": "all",
            "daterange": "all",
            "num": page,
            "item": book_id
        }

        try:
            response = session.post(api_url, headers=headers, data=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # 關鍵修正：博客來回傳的欄位名稱叫 'htmlData'
                html_content = data.get('htmlData', '')
                
                if not html_content or '<div class="box-item' not in html_content:
                    print(f"⚠️ 第 {page} 頁沒有更多評論內容。")
                    break
                
                soup = BeautifulSoup(html_content, 'html.parser')
                comments = soup.select('div.box-item')
                
                for idx, item in enumerate(comments):
                    # 1. 評論者姓名
                    name_tag = item.select_one('.user .name a')
                    reviewer_name = name_tag.text.strip() if name_tag else "Unknown"
                    
                    # 2. 評分 (例如 5.0)
                    rating_tag = item.select_one('.detail div')
                    rating = rating_tag.text.strip() if rating_tag else ""
                    
                    # 3. 評論日期
                    date_tag = item.select_one('.date')
                    review_date = date_tag.text.strip() if date_tag else ""
                    
                    # 4. 評論內容 (處理那個經典的 calss 拼錯)
                    content_tag = item.select_one('span[calss="comment-content"]') or item.select_one('span.comment-content')
                    if not content_tag:
                        # 備案：抓取 description 區塊
                        desc_tag = item.select_one('.description')
                        review_text = desc_tag.get_text(strip=True) if desc_tag else ""
                    else:
                        review_text = content_tag.get_text(strip=True)

                    if len(review_text) < 2: continue
                        
                    reviews_data.append({
                        "review_id": f"{book_id}_{page}_{idx}",
                        "reviewer_name": reviewer_name,
                        "rating": rating,
                        "review_date": review_date,
                        "review": review_text
                    })
                
                print(f"✅ 第 {page} 頁成功，本頁抓取 {len(comments)} 則，累計 {len(reviews_data)} 則。")
            else:
                print(f"❌ HTTP 錯誤: {response.status_code}")
                break
                
            time.sleep(2.5) # 稍微停頓避免被鎖

        except Exception as e:
            print(f"❌ 抓取異常: {e}")
            break

    # --- 第三階段：存檔 ---
    if reviews_data:
        df = pd.DataFrame(reviews_data)
        # 移除完全重複的評論
        df.drop_duplicates(subset=['review'], inplace=True)
        if book_name:

            safe_book_name = "".join([

                c

                for c in book_name

                if c not in [
                    '/',
                    '\\',
                    ':',
                    '*',
                    '?',
                    '"',
                    '<',
                    '>',
                    '|'
                ]
            ])

            folder_path = os.path.join(

                "data",

                safe_book_name
            )

            os.makedirs(

                folder_path,

                exist_ok=True
            )

            csv_path = os.path.join(

                folder_path,

                f"{safe_book_name}_"

                f"{book_id}_reviews.csv"
            )
        else:
            csv_path = f"data/{book_id}_reviews.csv"
            
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n✨ 完美完成！共抓取 {len(df)} 則評論，存檔於：{csv_path}")
    else:
        print("\n💀 抓取結束，但沒有存入任何資料。")

if __name__ == "__main__":

    print("=== 博客來書評爬蟲 ===")

    url_input = input(
        "請輸入博客來網址: "
    ).strip()

    book_id_input = extract_book_id(
        url_input
    )

    if not book_id_input:

        print("❌ 網址格式錯誤")
        exit()

    book_name_input = input(
        "請輸入書名: "
    ).strip()

    pages_input = input(
        "請輸入最多抓取頁數: "
    ).strip()

    max_pages_val = (
        int(pages_input)
        if pages_input.isdigit()
        else 10
    )

    crawl_book_reviews(

        book_id=book_id_input,

        book_name=book_name_input,

        max_pages=max_pages_val
    )