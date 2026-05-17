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


def analyze_sentiment(
    file_path,
    book_name
):

    try:

        df = pd.read_csv(file_path)

    except Exception as e:

        print(f"讀取錯誤: {e}")

        return None

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

        default_language="zh-Hant"
    )

    all_sentiments = []

    all_scores = []

    texts = df["processed_text"].tolist()

    batch_size = 10

    for i in range(
        0,
        len(texts),
        batch_size
    ):

        batch = texts[
            i:i + batch_size
        ]

        clean_batch = [

            str(t)

            if str(t).strip() != "nan"

            else "無"

            for t in batch
        ]

        response = client.analyze_sentiment(
            documents=clean_batch
        )

        for doc in response:

            if not doc.is_error:

                all_sentiments.append(
                    doc.sentiment
                )

                all_scores.append(

                    round(
                        doc.confidence_scores.positive,
                        2
                    )
                )

            else:

                all_sentiments.append(
                    "neutral"
                )

                all_scores.append(0.5)

    df["sentiment"] = all_sentiments

    df["sentiment_score"] = all_scores

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

        f"sentiment_result_"

        f"{safe_book_name}.csv"
    )

    df.to_csv(

        output_path,

        index=False,

        encoding="utf-8-sig"
    )

    print("情緒分析已輸出:", output_path)

    return df


if __name__ == "__main__":

    result = analyze_sentiment(

        "data/前處理_牧羊少年奇幻之旅.csv",

        book_name="牧羊少年奇幻之旅"
    )

    print(result)