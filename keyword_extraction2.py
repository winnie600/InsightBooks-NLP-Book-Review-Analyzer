# file: keyword_extraction2.py

from collections import Counter

import pandas as pd

from wordcloud import WordCloud

import matplotlib.pyplot as plt

import os

def extract_keywords(
    df,
    book_name,
):

    if "pos_text" not in df.columns:

        raise ValueError(
            "df 必須包含 pos_text 欄位"
        )

    all_keywords = []

    # ===== 擷取名詞與形容詞 =====

    for text in df["pos_text"]:

        if not isinstance(text, str):
            continue

        for pair in text.split():

            if "/" not in pair:
                continue

            word, pos = pair.split("/", 1)

            if (
                pos.startswith("n")
                or pos.startswith("a")
            ) and len(word) > 1:

                all_keywords.append(word)

    # ===== 詞頻統計 =====

    word_freq = Counter(all_keywords)

    # 文字雲使用較多詞
    most_common = word_freq.most_common(30)

    # 網頁 badge 顯示前 5
    keywords = [

        word

        for word, _

        in most_common[:5]
    ]



    # ===== 產生文字雲 =====

    text = " ".join(all_keywords)

    safe_book_name = "".join(

        c for c in book_name

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
    )
    # ===== 建立資料夾 =====

    folder_path = (
        f"data/{safe_book_name}"
    )

    os.makedirs(
        folder_path,
        exist_ok=True
    )

    # ===== 路徑 =====

    output_path = (

        f"{folder_path}/"

        f"keywords_result_"

        f"{safe_book_name}.csv"
    )

    image_path = (
        f"static/wordcloud_"
        f"{safe_book_name}.png"
    )
    # ===== 匯出 CSV =====

    output_df = pd.DataFrame({

        "top_keywords": keywords

    })

    output_df.to_csv(

        output_path,

        index=False,

        encoding="utf-8-sig"
    )

    print("CSV 已輸出:", output_path)

    wc = WordCloud(

        font_path="C:/Windows/Fonts/msjh.ttc",

        width=1000,

        height=500,

        background_color="white",

        max_words=100

    ).generate(text)

    plt.figure(figsize=(12, 6))

    plt.imshow(

        wc,

        interpolation="bilinear"
    )

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(

        image_path,

        dpi=150
    )

    plt.close()

    print("文字雲已輸出:", image_path)

    # ===== 回傳 =====

    result = {

        "top_keywords": keywords,

        "wordcloud_image":
            image_path
    }

    return result


# =========================
# 測試用
# =========================

if __name__ == "__main__":

    df = pd.read_csv(
        "data/前處理_解憂雜貨店.csv"
    )

    result = extract_keywords(

        df,

        book_name="解憂雜貨店"
    )
    print(result)