import re
import requests
import pandas as pd
import os

from bs4 import BeautifulSoup

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from input_crawler import (
    crawl_book_reviews
)

from preprocessing import (
    preprocess_csv
)

from summarization import (
    summarize_reviews
)

from sentiment_analysis import (
    analyze_sentiment
)

from keyword_extraction2 import (
    extract_keywords
)

from text_classification import (
    classify_text
)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")




@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.json

    url = data.get("url")

    preset = data.get("preset")

    # =========================
    # URL 模式
    # =========================

    if url:

        match = re.search(

            r'/products/(\d+)',

            url
        )

        if not match:

            return jsonify({
                "error": "博客來網址格式錯誤"
            }), 400

        book_id = match.group(1)

        # ===== 自動抓書名 =====

        product_url = (
            f"https://www.books.com.tw/products/{book_id}"
        )

        response = requests.get(product_url)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title_tag = soup.select_one("h1")

        book_name = (

            title_tag.text.strip()

            if title_tag

            else book_id
        )

        book_name = re.split(

            r"[（(]",

            book_name

        )[0].strip()
        
        # ===== 避免 Windows 檔名錯誤 =====

        book_name = "".join(

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


        try:

            # ===== 爬蟲 =====

            crawl_book_reviews(

                book_id=book_id,

                book_name=book_name,

                max_pages=5
            )

            # ===== 前處理 =====

            raw_csv = (

                f"data/{book_name}/"

                f"{book_name}_"

                f"{book_id}_reviews.csv"
            )

            processed_df = preprocess_csv(

                raw_csv,

                book_title=book_name
            )

            if processed_df is None:

                return jsonify({
                    "error": "前處理失敗"
                }), 500

            folder_path = (
                f"data/{book_name}"
            )

            os.makedirs(
                folder_path,
                exist_ok=True
            )

            processed_output = (

                f"{folder_path}/"

                f"前處理_{book_name}.csv"
            )

            processed_df.to_csv(

                processed_output,

                index=False,

                encoding="utf-8-sig"
            )

            # ===== Keyword =====

            keyword_result = extract_keywords(
                processed_df,
                book_name=book_name,
            )

            keywords = keyword_result[
                "top_keywords"
            ]


            # ===== Text Classification =====

            classify_text(

                processed_output,

                book_name

            )
            
            classification_df = pd.read_csv(

                f"data/{book_name}/"

                f"classified_result_"

                f"{book_name}.csv"

            )

            classification_counts=(

                classification_df[
                "category"
                ]

                .fillna("其他")

                .astype(str)

                .str.split(",")

                .explode()

                .value_counts()

                .to_dict()

            )

            # ===== Summary =====

            summary_df = summarize_reviews(
                processed_output,
                book_name=book_name
            )

            if summary_df is not None:

                rating_df = pd.read_csv(
                    processed_output
                )

                positive_rating_count = len(
                    rating_df[
                        rating_df["rating"] >= 4
                    ]
                )

                neutral_rating_count = len(
                    rating_df[
                        (rating_df["rating"] >= 3)
                        &
                        (rating_df["rating"] < 4)
                    ]
                )

                negative_rating_count = len(
                    rating_df[
                        rating_df["rating"] < 3
                    ]
                )

                summary_text = {

                    "positive":{

                        "text":
                        summary_df[
                        "positive_summary"
                        ][0],

                        "count":
                        positive_rating_count

                    },

                    "neutral":{

                        "text":
                        summary_df[
                        "neutral_summary"
                        ][0],

                        "count":
                        neutral_rating_count

                    },

                    "negative":{

                        "text":
                        summary_df[
                        "negative_summary"
                        ][0],

                        "count":
                        negative_rating_count

                    }

                }

            else:

                summary_text = (
                    "摘要失敗"
                )

            # ===== Sentiment =====

            sentiment_df = analyze_sentiment(
                processed_output,
                book_name=book_name
            )

            positive_count = (
                sentiment_df["sentiment"] == "positive"
            ).sum()

            neutral_count = (
                sentiment_df["sentiment"] == "neutral"
            ).sum()

            negative_count = (
                sentiment_df["sentiment"] == "negative"
            ).sum()

            total = len(sentiment_df)

            sentiment = {

                "positive": {

                    "count":
                        int(positive_count),

                    "percent":
                        round(
                            positive_count / total * 100,
                            1
                        )
                },

                "neutral": {

                    "count":
                        int(neutral_count),

                    "percent":
                        round(
                            neutral_count / total * 100,
                            1
                        )
                },

                "negative": {

                    "count":
                        int(negative_count),

                    "percent":
                        round(
                            negative_count / total * 100,
                            1
                        )
                }
            }

            review_df = sentiment_df.copy()

            review_df["category"] = (
                classification_df["category"]
                .fillna("其他")
            )

            return jsonify({

                "summary": summary_text,
                "classification": classification_counts,

                "reviews":

                review_df[
                    [
                        "rating",
                        "review_cleaned",
                        "sentiment",
                        "category"
                    ]
                ]

                .fillna("")

                .to_dict(
                    orient="records"
                ),

                "keywords": keywords,

                "wordcloud":
                    keyword_result[
                        "wordcloud_image"
                    ],

                "sentiment": sentiment,

                "book": book_name
            })

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500

    # =========================
    # 預設書籍模式
    # =========================

    if not preset:

        return jsonify({
            "error": "未選擇書籍"
        }), 400

    base_path = f"data/{preset}"

    processed_path = (

        f"{base_path}/"

        f"前處理_{preset}.csv"

    )

    # ===== Text Classification =====

    classify_text(

        processed_path,

        preset

    )


    classification_df = pd.read_csv(

    f"{base_path}/"

    f"classified_result_"

    f"{preset}.csv"

    )

    classification_counts=(

    classification_df[
    "category"
    ]

    .str.split(",")

    .explode()

    .value_counts()

    .to_dict()

    )

    # ===== Summary =====

    summary_df = pd.read_csv(

        f"{base_path}/"

        f"summary_output_{preset}.csv"
    )

    rating_df = pd.read_csv(

        f"{base_path}/"

        f"前處理_{preset}.csv"
    )

    positive_rating_count = len(
        rating_df[
            rating_df["rating"] >= 4
        ]
    )

    neutral_rating_count = len(
        rating_df[
            (rating_df["rating"] >= 3)
            &
            (rating_df["rating"] < 4)
        ]
    )

    negative_rating_count = len(
        rating_df[
            rating_df["rating"] < 3
        ]
    )

    summary_text = {

        "positive":{

            "text":

            summary_df.get(
                "positive_summary",
                pd.Series([
                "目前沒有好評資料"
                ])
            ).iloc[0],

            "count":
            positive_rating_count

        },

        "neutral":{

            "text":

            summary_df.get(
                "neutral_summary",
                pd.Series([
                "目前沒有普通評論"
                ])
            ).iloc[0],

            "count":
            neutral_rating_count

        },

        "negative":{

            "text":

            summary_df.get(
                "negative_summary",
                pd.Series([
                "目前沒有負評資料"
                ])
            ).iloc[0],

            "count":
            negative_rating_count

        }

    }

    # ===== Keywords =====

    base_path = f"data/{preset}"

    keyword_df = pd.read_csv(

        f"{base_path}/"

        f"keywords_result_{preset}.csv"
    )

    keywords = keyword_df[
        "top_keywords"
    ].tolist()

    # ===== Sentiment =====

    sentiment_df = pd.read_csv(

        f"{base_path}/"

        f"sentiment_result_{preset}.csv"
    )

    positive_count = (
        sentiment_df["sentiment"] == "positive"
    ).sum()

    neutral_count = (
        sentiment_df["sentiment"] == "neutral"
    ).sum()

    negative_count = (
        sentiment_df["sentiment"] == "negative"
    ).sum()

    total = len(sentiment_df)

    review_df = sentiment_df.copy()

    review_df["category"] = (
        classification_df["category"]
        .fillna("其他")
    )

    result = {

        "reviews":

        review_df[
            [
                "rating",
                "review_cleaned",
                "sentiment",
                "category"
            ]
        ]

        .fillna("")

        .to_dict(
            orient="records"
        ),

    "summary": summary_text,

    "classification":
    classification_counts,

    "keywords":
    keywords[:10],

    "wordcloud":
    f"/static/wordcloud_{preset}.png",

    "sentiment":{

    "positive":{

    "count":
    int(
    positive_count
    ),

    "percent":
    round(
    positive_count
    /
    total
    *
    100,
    1
    )

    },

    "neutral":{

    "count":
    int(
    neutral_count
    ),

    "percent":
    round(
    neutral_count
    /
    total
    *
    100,
    1
    )

    },

    "negative":{

    "count":
    int(
    negative_count
    ),

    "percent":
    round(
    negative_count
    /
    total
    *
    100,
    1
    )

    }

    },

    "book":
    preset

    }

    return jsonify(result)

# =========================
# Pipeline
# =========================

@app.route("/pipeline")
def pipeline():

    book = request.args.get("book")

    page = request.args.get(
        "page",
        default=1,
        type=int
    )

    per_page = 10

    processed_df = pd.read_csv(

        f"data/{book}/"

        f"前處理_{book}.csv"

    ).fillna("")

    total_reviews = len(processed_df)

    total_pages = (
        total_reviews + per_page - 1
    ) // per_page

    start = (page - 1) * per_page

    end = start + per_page

    page_df = processed_df.iloc[
        start:end
    ]

    return render_template(

        "pipeline.html",

        book=book,

        processed_data=page_df.to_dict(
            orient="records"
        ),

        page=page,

        total_pages=total_pages
    )


if __name__ == "__main__":

    app.run(debug=True)
