import pandas as pd
import jieba
import jieba.posseg as pseg
import re
import os

def load_stopwords(filepath='stopwords.txt'):
    stopwords = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word: stopwords.add(word)
    return stopwords

def basic_clean(text):
    """最輕度清理：只移除 HTML 標籤和過多的空白，保留標點符號供【摘要】使用"""
    if not isinstance(text, str): return ""
    text = re.sub(r'<[^>]+>', '', text)  # 移除 HTML
    text = re.sub(r'\s+', ' ', text)      # 壓縮空白
    return text.strip()

def word_only_clean(text):
    """深度清理：移除所有標點符號，只留文字與數字供【關鍵字分析】使用"""
    text = re.sub(r'[^\w\u4e00-\u9fa5]', '', text)
    return text

def preprocess_csv(csv_path, book_title="被討厭的勇氣"):#修改書名
    if not os.path.exists(csv_path):
        print(f"❌ 找不到檔案：{csv_path}")
        return None

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    stopwords = load_stopwords('stopwords.txt')
    
    # 這裡要注意：如果你的停用詞表有「否定詞」，情緒分析會壞掉
    # 建議情緒分析隊友檢查一下：negation_words = ['不', '沒', '無', '非']
    
    cleaned_reviews = []    # 給摘要用的 (含標點)
    processed_texts = []    # 給關鍵字用的 (空格分隔)
    pos_texts = []          # 給詞性標註用的

    for text in df['review']:
        # 1. 給摘要用的輕度清理
        b_clean = basic_clean(text)
        cleaned_reviews.append(b_clean)
        
        # 2. 分詞與詞性標註
        # 使用 word_only_clean 確保分詞時不被奇怪符號干擾
        words_with_pos = pseg.lcut(word_only_clean(b_clean))
        
        filtered_words = []
        filtered_pos = []
        for word, flag in words_with_pos:
            if word not in stopwords and len(word) > 0:
                filtered_words.append(word)
                filtered_pos.append(f"{word}/{flag}")
        
        processed_texts.append(" ".join(filtered_words))
        pos_texts.append(" ".join(filtered_pos))

    # 寫入 DataFrame
    df['book_title'] = book_title
    df['review_cleaned'] = cleaned_reviews
    df['processed_text'] = processed_texts
    df['pos_text'] = pos_texts
    
    # --- 最終交付欄位組合 ---
    # 保留 rating 是為了讓隊友能驗證情緒分析準不準 (例如 5 星通常是正向)
    output_cols = ["review_id", "book_title", "rating", "review_cleaned", "processed_text", "pos_text"]
    
    return df[output_cols]

if __name__ == "__main__":

    file_name = input(
        "請輸入要前處理的 CSV 檔名："
    ).strip()

    book_title = input(
        "請輸入書名："
    ).strip()

    input_path = os.path.join(
        "data",
        file_name
    )

    df_final = preprocess_csv(

        input_path,

        book_title=book_title
    )

    if df_final is not None:

        folder_path = os.path.join(

            "data",

            book_title
        )

        os.makedirs(

            folder_path,

            exist_ok=True
        )

        output_path = os.path.join(

            folder_path,

            f"前處理_{book_title}.csv"
        )

        df_final.to_csv(

            output_path,

            index=False,

            encoding="utf-8-sig"
        )

        print(

            "\n✨ 前處理完成"

        )

        print(
            f"輸出位置：{output_path}"
        )

    else:

        print(
            "❌ 前處理失敗"
        )