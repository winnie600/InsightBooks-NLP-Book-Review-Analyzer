import pandas as pd
import os


def classify_text(
    file_path,
    book_name
):

    """
    書評分類模組

    分類：
    內容品質分析
    翻譯品質分析
    實用性評估
    閱讀體驗分析
    價格與CP值分析
    """

    # 讀 CSV

    try:

        df = pd.read_csv(
            file_path
        )

    except Exception as e:

        print(
            f"讀取錯誤:{e}"
        )

        return None

    # 關鍵字規則

    category_keywords = {

        "內容品質分析":[

            "劇情",
            "文筆",
            "架構",
            "內容",
            "故事",
            "深度",
            "知識",
            "邏輯"

        ],

        "翻譯品質分析":[

            "翻譯",
            "譯者",
            "流暢",
            "語法",
            "生硬",
            "原文",
            "措辭",
            "誤譯"

        ],

        "實用性評估":[

            "教學",
            "技巧",
            "方法",
            "工具",
            "實用",
            "操作",
            "收穫",
            "學習",
            "範例"

        ],

        "閱讀體驗分析":[

            "排版",
            "印刷",
            "封面",
            "字體",
            "紙質",
            "間距",
            "美觀",
            "手感"

        ],

        "價格與CP值分析":[

            "價格",
            "划算",
            "便宜",
            "特價",
            "CP值",
            "貴",
            "折扣",
            "值回票價"

        ]

    }

    # 找評論欄位

    possible_cols = [

        "processed_text",

        "review_cleaned",

        "review"

    ]

    target_col = None

    for col in possible_cols:

        if col in df.columns:

            target_col = col

            break

    if target_col is None:

        raise ValueError(
            "找不到評論欄位"
        )

    # 分類函數

    def get_label(text):

        text = str(text)

        matched = []

        for cat, words in (
            category_keywords
            .items()
        ):

            if any(

                word in text

                for word in words

            ):

                matched.append(
                    cat
                )

        return (

            ",".join(
                matched
            )

            if matched

            else "其他"

        )

    # 新欄位

    df[
        "category"
    ] = df[
        target_col
    ].apply(
        get_label
    )

    # 建資料夾

    safe_book_name = "".join(

        c

        for c

        in book_name

        if c not in [

            "/",
            "\\",
            ":",
            "*",
            "?",
            "\"",
            "<",
            ">",
            "|"

        ]

    )

    folder_path = (

        f"data/"

        f"{safe_book_name}"

    )

    os.makedirs(

        folder_path,

        exist_ok=True

    )

    output_path = (

        f"{folder_path}/"

        f"classified_result_"

        f"{safe_book_name}.csv"

    )

    # 匯出

    try:

        df.to_csv(

            output_path,

            index=False,

            encoding=
            "utf-8-sig"

        )

        print(

            "分類完成:",

            output_path

        )

    except Exception as e:

        print(
            f"輸出失敗:{e}"
        )

    return df


if __name__ == "__main__":

    result = classify_text(

        file_path=

        "data/原子習慣/"

        "前處理_原子習慣.csv",

        book_name=
        "原子習慣"

    )

    print(

        result[
            [
                "category"
            ]
        ].head()

    )