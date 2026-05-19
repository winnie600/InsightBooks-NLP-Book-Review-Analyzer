let sentimentChart = null;
let classificationChart = null;

async function analyzeBook() {
    const url =
        document.getElementById(
            "urlInput"
        ).value;

    const preset =
        document.getElementById(
            "presetSelect"
        ).value;

    document.getElementById(
        "loading"
    ).style.display = "block";

    try {
        const response =
            await fetch(
                "/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            url,
                            preset
                        })
                }
            );

        const text =
            await response.text();

        console.log(
            "backend:",
            text
        );

        if (!response.ok) {

            throw new Error(
                text
            );

        }

        const data =
            JSON.parse(
                text
            );

        window.currentBook =
            data.book;

        window.lastAnalysisData =
            data;

        initReviewExplorer(data);

        updateWordCloud(data);

        updateSentimentText(data);

        createSentimentChart(data);

        updateKeywordList(data);


        updateSummary(data);
    }

    catch (error) {
        console.error(error);

        alert(
            "分析失敗"
        );
    }

    finally {
        document.getElementById(
            "loading"
        ).style.display =
            "none";
    }
}


function initReviewExplorer(
    data
) {

    const selector =
        document.getElementById(
            "reviewSelector"
        );

    selector.innerHTML = "";

    data.reviews.forEach(
        (
            review,
            index
        ) => {

            selector.innerHTML += `

            <option
                value="${index}"
            >

                ⭐${review.rating}

                評論

                ${index + 1}

            </option>

            `;
        }
    );

    createClassificationChart(
        data
    );

    selector.onchange =
        () => {

            const review =
                data.reviews[
                    selector.value
                ];

            updateReviewPreview(
                review
            );

            updateSentimentHighlight(
                review
            );

            updateClassificationHighlight(
                review,
                data
            );
        };

    if (
        data.reviews.length
    ) {
        selector.value = 0;

        selector.onchange();
    }
}


function updateReviewPreview(
    review
) {

    document
        .getElementById(
            "reviewPreview"
        )

        .innerText =

        review.review_cleaned;
}


function updateSentimentHighlight(
    review
) {

    document
        .querySelectorAll(
            ".sentiment-item"
        )

        .forEach(
            item =>
                item.classList.remove(
                    "active-highlight"
                )
        );

    if (
        review.sentiment ===
        "positive"
    ) {

        document
            .getElementById(
                "positiveItem"
            )

            .classList.add(
                "active-highlight"
            );
    }

    else if (
        review.sentiment ===
        "neutral"
    ) {

        document
            .getElementById(
                "neutralItem"
            )

            .classList.add(
                "active-highlight"
            );
    }

    else {

        document
            .getElementById(
                "negativeItem"
            )

            .classList.add(
                "active-highlight"
            );
    }
}


function createClassificationChart(
    data
) {

    const canvas =
        document.getElementById(
            "classificationChart"
        );

    if (
        classificationChart
    ) {

        classificationChart
            .destroy();

        classificationChart =
            null;
    }

    classificationChart =
        new Chart(

            canvas.getContext(
                "2d"
            ),

            {
                type: "bar",

                data: {

                    labels:

                        Object.keys(
                            data.classification
                        ),

                    datasets: [
                        {
                            label:
                                "評論數",

                            data:

                                Object.values(
                                    data.classification
                                ),

                            backgroundColor:

                                Object.keys(
                                    data.classification
                                )

                                    .map(
                                        () =>
                                            "#E7E2DC"
                                    ),

                            borderRadius:
                                12,

                            barThickness:
                                24
                        }
                    ]
                },

                options: {

                    indexAxis:
                        "y",

                    responsive:
                        true,

                    plugins: {

                        legend: {
                            display:
                                false
                        }
                    },

                    scales: {

                        x: {
                            grid: {
                                display:
                                    false
                            }
                        },

                        y: {
                            grid: {
                                display:
                                    false
                            }
                        }
                    }
                }
            }
        );
}


function updateClassificationHighlight(
    review,
    data
) {

    window.selectedCategory =

        review.category

            ?.split(",")

            .map(
                item =>
                    item.trim()
            );

    if (
        !classificationChart
    ) {
        return;
    }

    classificationChart
        .data
        .datasets[0]
        .backgroundColor =

        Object.keys(
            data.classification
        )

            .map(

                category =>

                    window
                        .selectedCategory

                        ?.includes(
                            category
                        )

                        ?

                        "#A8B5A2"

                        :

                        "#E7E2DC"
            );

    classificationChart
        .update();
}


function updateWordCloud(
    data
) {

    document
        .getElementById(
            "wordcloudImage"
        )

        .src =

        data.wordcloud +

        "?t=" +

        Date.now();
}

function updateKeywordList(
    data
) {

    const container =

        document.getElementById(
            "keywordContainer"
        );

    container.innerHTML = "";

    data.keywords.forEach(

        keyword => {

            container.innerHTML += `

            <span
                class="keyword-badge"
            >

                ${keyword}

            </span>

            `;
        }

    );

}


function updateSentimentText(
    data
) {

    document
        .getElementById(
            "positiveText"
        )

        .innerText =

        `${data.sentiment
            .positive.count}則

        (${data.sentiment.positive.percent}%)`;


    document
        .getElementById(
            "neutralText"
        )

        .innerText =

        `${data.sentiment
            .neutral.count}則

        (${data.sentiment.neutral.percent}%)`;


    document
        .getElementById(
            "negativeText"
        )

        .innerText =

        `${data.sentiment
            .negative.count}則

        (${data.sentiment.negative.percent}%)`;
}


function createSentimentChart(
    data
) {

    const canvas =
        document.getElementById(
            "sentimentChart"
        );

    if (
        sentimentChart
    ) {

        sentimentChart
            .destroy();

        sentimentChart =
            null;
    }

    sentimentChart =
        new Chart(
            canvas,
            {
                type: "pie",

                data: {

                    labels: [

                        `Positive
                        (${data.sentiment.positive.count})`,

                        `Neutral
                        (${data.sentiment.neutral.count})`,

                        `Negative
                        (${data.sentiment.negative.count})`
                    ],

                    datasets: [
                        {
                            data: [

                                data
                                    .sentiment
                                    .positive
                                    .percent,

                                data
                                    .sentiment
                                    .neutral
                                    .percent,

                                data
                                    .sentiment
                                    .negative
                                    .percent
                            ]
                        }
                    ]
                }
            }
        );
}

function updateSummary(
    data
) {

    document
        .getElementById(
            "positiveSummary"
        )

        .innerText =

        data.summary
        .positive
        .text;


    document
        .getElementById(
            "neutralSummary"
        )

        .innerText =

        data.summary
        .neutral
        .text;


    document
        .getElementById(
            "negativeSummary"
        )

        .innerText =

        data.summary
        .negative
        .text;

}




function goToPipeline() {

    let targetBook =
        window.currentBook;

    if (
        !targetBook
    ) {

        targetBook =

            document
                .getElementById(
                    "presetSelect"
                )
                .value;
    }

    if (
        !targetBook
    ) {

        alert(
            "請先分析書籍"
        );

        return;
    }

    window.location.href =

        `/pipeline?book=${encodeURIComponent(
            targetBook
        )}`;
}
