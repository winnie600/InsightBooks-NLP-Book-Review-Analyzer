// file: static/js/main.js

let sentimentChart = null;

async function analyzeBook() {

    const url =
        document.getElementById("urlInput").value;

    const preset =
        document.getElementById("presetSelect").value;

    const response = await fetch("/analyze", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            url,
            preset
        })

    });

    const data = await response.json();
    console.log(data);
    // ===== 保存目前分析書籍 =====

    window.currentBook = data.book;

    // ===== Summary =====

    document.getElementById("summaryBox").innerText =
        data.summary;

    // ===== Keywords =====

    const keywordContainer =
        document.getElementById("keywordContainer");

    keywordContainer.innerHTML = "";

    data.keywords.forEach(keyword => {

        keywordContainer.innerHTML += `
            <span class="badge bg-primary m-1">
                ${keyword}
            </span>
        `;

    });

    // ===== Chart =====

    const ctx =
        document.getElementById("sentimentChart");

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    sentimentChart = new Chart(ctx, {

        type: "pie",

        data: {

            labels: [
                "Positive",
                "Neutral",
                "Negative"
            ],

            datasets: [{
                data: [
                    data.sentiment.positive,
                    data.sentiment.neutral,
                    data.sentiment.negative
                ]
            }]

        }

    });

}

function goToPipeline() {

    if (!window.currentBook) {

        const preset =
            document
            .getElementById(
                "presetSelect"
            )
            .value;

        if (!preset) {

            alert("請先分析書籍");

            return;
        }

        window.currentBook = preset;
    }

    window.location.href =
        `/pipeline?book=${encodeURIComponent(window.currentBook)}`;
}