import pandas as pd

from azure.core.credentials import (
    AzureKeyCredential
)

from azure.ai.textanalytics import (
    TextAnalyticsClient
)

from dotenv import load_dotenv

import os

load_dotenv()

endpoint = os.getenv(
    "AZURE_LANGUAGE_ENDPOINT"
)

key = os.getenv(
    "AZURE_LANGUAGE_KEY"
)

credential = AzureKeyCredential(key)

client = TextAnalyticsClient(

    endpoint=endpoint,

    credential=credential,

    default_language="zh"
)


def generate_summary(texts):

    texts = [

        t.strip()

        for t in texts

        if isinstance(t, str)

        and len(t.strip()) > 10
    ]

    if not texts:

        return "無足夠評論"

    full_text = "。".join(texts)

    full_text = full_text[:4500]

    try:

        poller = client.begin_abstract_summary(
            [full_text]
        )

        result = poller.result()

        summaries = []

        for doc in result:

            if not doc.is_error:

                for summary in doc.summaries:

                    summaries.append(
                        summary.text
                    )

        return " ".join(summaries)

    except Exception as e:

        print(f"摘要錯誤: {e}")

        return "摘要失敗"


def summarize_reviews(
    file_path,
    book_name
):

    try:

        df = pd.read_csv(file_path)

    except Exception as e:

        print(f"讀取錯誤: {e}")

        return None

    if "rating" not in df.columns:

        print("缺少 rating 欄位")

        return None

    positive_df = df[
        df["rating"] >= 4
    ]

    neutral_df = df[
        (df["rating"] >= 3)
        & (df["rating"] < 4)
    ]

    negative_df = df[
        df["rating"] < 3
    ]

    positive_summary = (

        generate_summary(
            positive_df[
                "review_cleaned"
            ].tolist()
        )

        if not positive_df.empty

        else "目前沒有足夠的好評資料"
    )

    neutral_summary = (

        generate_summary(
            neutral_df[
                "review_cleaned"
            ].tolist()
        )

        if not neutral_df.empty

        else "目前沒有普通評論"
    )

    negative_summary = (

        generate_summary(
            negative_df[
                "review_cleaned"
            ].tolist()
        )

        if not negative_df.empty

        else "目前沒有負評資料"
    )

    result_df = pd.DataFrame({

        "positive_summary": [
            positive_summary
        ],

        "neutral_summary": [
            neutral_summary
        ],

        "negative_summary": [
            negative_summary
        ]
    })

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

    folder_path = (
        f"data/{safe_book_name}"
    )

    os.makedirs(
        folder_path,
        exist_ok=True
    )

    output_path = (

        f"{folder_path}/"

        f"summary_output_"

        f"{safe_book_name}.csv"
    )

    result_df.to_csv(

        output_path,

        index=False,

        encoding="utf-8-sig"
    )

    print("摘要已輸出:", output_path)

    return result_df


if __name__ == "__main__":

    result = summarize_reviews(

        "data/前處理_原子習慣.csv",

        book_name="原子習慣"
    )

    print(result)