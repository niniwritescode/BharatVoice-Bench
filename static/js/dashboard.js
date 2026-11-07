document.addEventListener("DOMContentLoaded", () => {
    // Read Flask-provided experiment data safely
    const dataElement = document.getElementById("chart-data");

    let ALL_RECORDS = [];

    if (dataElement) {
        try {
            ALL_RECORDS = JSON.parse(dataElement.textContent);
        } catch (error) {
            console.error("Could not read chart data:", error);
        }
    }
    // -----------------------------------------
    // 1. Animated metric counters
    // -----------------------------------------

    document.querySelectorAll("[data-count]").forEach(element => {
        const target = Number(element.dataset.count);

        if (!Number.isFinite(target)) return;

        const duration = 900;
        const start = performance.now();
        const decimals = String(element.dataset.count).includes(".") ? 2 : 0;

        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);

            element.textContent = (target * eased).toFixed(decimals);

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = target.toFixed(decimals);
            }
        }

        requestAnimationFrame(update);
    });


    // -----------------------------------------
    // 2. Recording search and filters
    // -----------------------------------------

    const table = document.getElementById("recordingsTable");

    if (table) {
        const rows = [...table.querySelectorAll(".record-row")];

        const search = document.getElementById("recordSearch");
        const language = document.getElementById("languageFilter");
        const speaker = document.getElementById("speakerFilter");
        const noise = document.getElementById("noiseFilter");
        const reset = document.getElementById("resetFilters");
        const count = document.getElementById("recordCount");
        const empty = document.getElementById("noResults");

        function populate(select, attribute) {
            const values = [...new Set(
                rows.map(row => row.dataset[attribute])
                    .filter(Boolean)
            )].sort();

            values.forEach(value => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent =
                    value.charAt(0).toUpperCase() + value.slice(1);
                select.appendChild(option);
            });
        }

        populate(language, "language");
        populate(speaker, "speaker");
        populate(noise, "noise");

        function filterRows() {
            const term = search.value.toLowerCase().trim();
            let visible = 0;

            rows.forEach(row => {
                const match =
                    row.dataset.search.includes(term) &&
                    (!language.value ||
                        row.dataset.language === language.value) &&
                    (!speaker.value ||
                        row.dataset.speaker === speaker.value) &&
                    (!noise.value ||
                        row.dataset.noise === noise.value);

                row.classList.toggle("d-none", !match);

                if (match) visible++;
            });

            count.textContent = visible;

            if (empty) {
                empty.classList.toggle("d-none", visible !== 0);
            }
        }

        [search, language, speaker, noise].forEach(control => {
            control.addEventListener("input", filterRows);
            control.addEventListener("change", filterRows);
        });

        reset.addEventListener("click", () => {
            search.value = "";
            language.value = "";
            speaker.value = "";
            noise.value = "";
            filterRows();
        });
    }


    // -----------------------------------------
    // 3. Back-to-top button
    // -----------------------------------------

    const backToTop = document.getElementById("backToTop");

    if (backToTop) {
        window.addEventListener("scroll", () => {
            backToTop.classList.toggle("visible", window.scrollY > 350);
        });

        backToTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }


    // -----------------------------------------
    // 4. Homepage 3D mouse movement
    // -----------------------------------------

    const visual = document.getElementById("soundVisual");

    if (visual && window.matchMedia("(pointer: fine)").matches) {
        const hero = visual.closest(".hero-section");

        hero.addEventListener("mousemove", event => {
            const rect = visual.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;

            visual.style.transform =
                `rotateY(${x * 9}deg) rotateX(${-y * 9}deg)`;
        });

        hero.addEventListener("mouseleave", () => {
            visual.style.transform = "rotateY(0deg) rotateX(0deg)";
        });
    }


    // -----------------------------------------
    // 5. Plotly interactive analytics
    // -----------------------------------------

    if (
    !Array.isArray(ALL_RECORDS) ||
    typeof Plotly === "undefined"
) {
    console.error("Chart data or Plotly library is unavailable.");
    return;
}

    const dimensions = {
        language: {
            element: "chartLanguage",
            chart: "languageChart",
            title: "WER by language",
            field: "language"
        },
        noise: {
            element: "chartNoise",
            chart: "noiseChart",
            title: "WER by noise type",
            field: "noise"
        },
        snr: {
            element: "chartSnr",
            chart: "snrChart",
            title: "WER by SNR",
            field: "snr"
        },
        speaker: {
            element: "chartSpeaker",
            chart: "speakerChart",
            title: "WER by speaker",
            field: "speaker"
        }
    };

    const colors = [
        "#8B5CF6",
        "#38BDF8",
        "#2DD4BF",
        "#F59E0B",
        "#EC4899"
    ];

    const records = ALL_RECORDS.filter(record =>
        Number.isFinite(Number(record.wer))
    );

    const filters = {};

    Object.entries(dimensions).forEach(([key, config]) => {
        const select = document.getElementById(config.element);
        if (!select) return;

        filters[key] = select;

        const values = [...new Set(
            records.map(record => String(record[config.field]))
        )].sort((a, b) => {
            if (key === "snr") return parseInt(a) - parseInt(b);
            return a.localeCompare(b);
        });

        values.forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent =
                value.charAt(0).toUpperCase() + value.slice(1);
            select.appendChild(option);
        });
    });

    const recordMetric = document.getElementById("recordMetric");
    const meanMetric = document.getElementById("meanWerMetric");
    const corpusMetric = document.getElementById("corpusWerMetric");
    const languageMetric = document.getElementById("languageMetric");

    function getFilteredRecords() {
        return records.filter(record => {
            return Object.entries(dimensions).every(([key, config]) => {
                const selected = filters[key]?.value;

                return !selected ||
                    String(record[config.field]) === selected;
            });
        });
    }

    function calculateMetrics(data) {
        const count = data.length;

        if (!count) {
            return {
                count: 0,
                mean: 0,
                corpus: 0,
                languages: 0
            };
        }

        const mean = data.reduce(
            (sum, record) => sum + Number(record.wer), 0
        ) / count;

        const substitutions = data.reduce(
            (sum, record) => sum + Number(record.substitutions || 0), 0
        );

        const deletions = data.reduce(
            (sum, record) => sum + Number(record.deletions || 0), 0
        );

        const insertions = data.reduce(
            (sum, record) => sum + Number(record.insertions || 0), 0
        );

        const words = data.reduce(
            (sum, record) => sum + Number(record.reference_words || 0), 0
        );

        const corpus = words
            ? ((substitutions + deletions + insertions) / words) * 100
            : 0;

        const languages = new Set(data.map(r => r.language)).size;

        return {
            count,
            mean,
            corpus,
            languages
        };
    }

    function updateMetrics(data) {
        const metrics = calculateMetrics(data);

        recordMetric.textContent = metrics.count;
        meanMetric.innerHTML = `${metrics.mean.toFixed(2)}<small>%</small>`;
        corpusMetric.innerHTML = `${metrics.corpus.toFixed(2)}<small>%</small>`;
        languageMetric.textContent = metrics.languages;
    }

    function groupRecords(data, field) {
        const groups = {};

        data.forEach(record => {
            const label = String(record[field]);

            if (!groups[label]) {
                groups[label] = [];
            }

            groups[label].push(record);
        });

        return Object.entries(groups).map(([label, items]) => {
            const meanWer = items.reduce(
                (sum, record) => sum + Number(record.wer), 0
            ) / items.length;

            const substitutions = items.reduce(
                (sum, record) => sum + Number(record.substitutions || 0), 0
            );

            const deletions = items.reduce(
                (sum, record) => sum + Number(record.deletions || 0), 0
            );

            const insertions = items.reduce(
                (sum, record) => sum + Number(record.insertions || 0), 0
            );

            const words = items.reduce(
                (sum, record) => sum + Number(record.reference_words || 0), 0
            );

            const corpusWer = words
                ? ((substitutions + deletions + insertions) / words) * 100
                : 0;

            return {
                label,
                meanWer,
                count: items.length,
                corpusWer,
                substitutions,
                deletions,
                insertions,
                words
            };
        }).sort((a, b) => {
            if (field === "snr") {
                return parseInt(a.label) - parseInt(b.label);
            }
            return a.label.localeCompare(b.label);
        });
    }

    function chartLayout(title) {
        return {
            title: {
                text: "",
                font: { color: "#E7EDF8" }
            },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: {
                family: "DM Sans, sans-serif",
                color: "#AAB8D0",
                size: 11
            },
            margin: {
                l: 52,
                r: 20,
                t: 22,
                b: 65
            },
            height: 330,
            xaxis: {
                title: "",
                color: "#AAB8D0",
                tickfont: { color: "#AAB8D0" },
                gridcolor: "rgba(148,163,184,0.08)",
                linecolor: "rgba(148,163,184,0.15)",
                automargin: true
            },
            yaxis: {
                title: "Mean WER (%)",
                color: "#AAB8D0",
                gridcolor: "rgba(148,163,184,0.13)",
                zerolinecolor: "rgba(148,163,184,0.15)",
                rangemode: "tozero"
            },
            hoverlabel: {
                bgcolor: "#17263D",
                bordercolor: "#8B5CF6",
                font: { color: "#FFFFFF", size: 12 }
            },
            showlegend: false,
            bargap: 0.42
        };
    }

    const plotConfig = {
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
        modeBarButtonsToRemove: [
            "lasso2d",
            "select2d"
        ],
        toImageButtonOptions: {
            format: "png",
            filename: "bharatvoice-chart",
            height: 700,
            width: 1100,
            scale: 2
        }
    };

    function renderChart(key, data) {
        const config = dimensions[key];
        const chartElement = document.getElementById(config.chart);

        if (!chartElement) return;

        const grouped = groupRecords(data, config.field);

        const labels = grouped.map(item => item.label);
        const values = grouped.map(item => item.meanWer);

        const customData = grouped.map(item => [
            item.count,
            item.corpusWer,
            item.substitutions,
            item.deletions,
            item.insertions,
            item.words
        ]);

        const trace = {
            type: "bar",
            x: labels,
            y: values,
            customdata: customData,
            marker: {
                color: labels.map((_, index) =>
                    colors[index % colors.length]
                ),
                opacity: 0.9,
                line: {
                    color: "rgba(255,255,255,0.18)",
                    width: 1
                }
            },
            text: values.map(value => `${value.toFixed(2)}%`),
            textposition: "outside",
            textfont: {
                color: "#DCE5F4",
                size: 11
            },
            hovertemplate:
                "<b>%{x}</b><br>" +
                "Mean record WER: %{y:.2f}%<br>" +
                "Records: %{customdata[0]}<br>" +
                "Corpus WER: %{customdata[1]:.2f}%<br>" +
                "Substitutions: %{customdata[2]}<br>" +
                "Deletions: %{customdata[3]}<br>" +
                "Insertions: %{customdata[4]}<br>" +
                "Reference words: %{customdata[5]}" +
                "<extra></extra>"
        };

        const layout = chartLayout(config.title);

        if (!grouped.length) {
            layout.annotations = [{
                text: "No records match these filters",
                x: 0.5,
                y: 0.5,
                xref: "paper",
                yref: "paper",
                showarrow: false,
                font: { color: "#AAB8D0", size: 13 }
            }];
        }

        Plotly.react(
            chartElement,
            [trace],
            layout,
            plotConfig
        );
    }

    function updateDashboard() {
        const filtered = getFilteredRecords();

        updateMetrics(filtered);

        Object.keys(dimensions).forEach(key => {
            renderChart(key, filtered);
        });
    }

    // Dropdown filters
    Object.values(filters).forEach(select => {
        select.addEventListener("change", updateDashboard);
    });

    // Clicking a bar applies that category as a filter.
    Object.entries(dimensions).forEach(([key, config]) => {
        const chartElement = document.getElementById(config.chart);

        if (!chartElement) return;

        chartElement.on("plotly_click", event => {
            if (!event.points || !event.points.length) return;

            const clickedValue = String(event.points[0].x);
            const select = filters[key];

            if (!select) return;

            // Click the selected category again to clear it.
            select.value =
                select.value === clickedValue ? "" : clickedValue;

            updateDashboard();
        });
    });

    // Reset all chart filters
    const resetCharts = document.getElementById("resetChartFilters");

    if (resetCharts) {
        resetCharts.addEventListener("click", () => {
            Object.values(filters).forEach(select => {
                select.value = "";
            });

            updateDashboard();
        });
    }

    // Initial chart rendering
    updateDashboard();

});