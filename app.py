
from flask import Flask, render_template
from pathlib import Path
import csv

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DATA_DIR = BASE_DIR / "public_data"


def load_csv(filename):
    file_path = PUBLIC_DATA_DIR / filename

    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def number(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def prepare_chart_records(rows):
    records = []

    for row in rows:
        wer_text = row.get("wer", "").strip()

        if not wer_text:
            continue

        records.append({
            "file": row.get("file", ""),
            "speaker": row.get("speaker", "Unknown"),
            "language": row.get("language", "Unknown").lower(),
            "noise": row.get("noise", "Unknown").lower(),
            "snr": row.get("snr", "Unknown"),
            "wer": number(wer_text),
            "substitutions": number(row.get("substitutions")),
            "deletions": number(row.get("deletions")),
            "insertions": number(row.get("insertions")),
            "reference_words": number(row.get("reference_words"))
        })

    return records


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analytics")
def analytics():
    results = load_csv("noisy_wer_summary.csv")
    records = prepare_chart_records(results)

    average_wer = (
        sum(record["wer"] for record in records) / len(records)
        if records else 0
    )

    total_errors = sum(
        record["substitutions"]
        + record["deletions"]
        + record["insertions"]
        for record in records
    )

    total_reference_words = sum(
        record["reference_words"] for record in records
    )

    corpus_wer = (
        total_errors / total_reference_words * 100
        if total_reference_words else 0
    )

    return render_template(
        "analytics.html",
        total_records=len(records),
        average_wer=round(average_wer, 2),
        corpus_wer=round(corpus_wer, 2),
        chart_records=records
    )


@app.route("/recordings")
def recordings():
    results = load_csv("noisy_wer_summary.csv")

    return render_template(
        "recordings.html",
        recordings=results
    )


@app.route("/methodology")
def methodology():
    return render_template("methodology.html")


if __name__ == "__main__":
    app.run(debug=True)
