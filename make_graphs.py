
import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt


# File paths
CSV_FILE = "results/noisy_wer_normalized.csv"
OUTPUT_DIR = "results/graphs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# Read CSV data
data = []

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if not row.get("wer"):
            continue

        data.append({
            "speaker": row["speaker"],
            "language": row["language"],
            "noise": row["noise"],
            "snr": row["snr"],
            "wer": float(row["wer"])
        })


if not data:
    raise ValueError("No valid WER records found in the CSV.")


# Calculate average WER for each category
def calculate_average(group_column):
    groups = defaultdict(list)

    for record in data:
        groups[record[group_column]].append(record["wer"])

    return {
        category: sum(scores) / len(scores)
        for category, scores in groups.items()
    }


# Common graph-generation function
def create_graph(title, xlabel, ylabel, filename, averages, order=None):

    categories = order if order else sorted(averages.keys())
    values = [averages[category] for category in categories]

    plt.figure(figsize=(9, 5))

    bars = plt.bar(categories, values, width=0.6)

    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.xticks(rotation=0)

    # Display percentage above each bar
    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(
        os.path.join(OUTPUT_DIR, filename),
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

    print(f"Created: {filename}")


# 1. WER by language
create_graph(
    title="ASR Performance by Language",
    xlabel="Language",
    ylabel="Average WER (%)",
    filename="wer_by_language.png",
    averages=calculate_average("language"),
    order=["english", "hindi", "hinglish"]
)


# 2. WER by noise type
create_graph(
    title="ASR Performance by Noise Type",
    xlabel="Background Noise",
    ylabel="Average WER (%)",
    filename="wer_by_noise.png",
    averages=calculate_average("noise"),
    order=["crowd", "fan", "traffic"]
)


# 3. WER by SNR
create_graph(
    title="ASR Performance at Different SNR Levels",
    xlabel="Signal-to-Noise Ratio",
    ylabel="Average WER (%)",
    filename="wer_by_snr.png",
    averages=calculate_average("snr"),
    order=["0dB", "10dB", "20dB"]
)


# 4. WER by speaker
create_graph(
    title="ASR Performance by Speaker",
    xlabel="Speaker",
    ylabel="Average WER (%)",
    filename="wer_by_speaker.png",
    averages=calculate_average("speaker"),
    order=["Nandini", "Shakun", "Ram"]
)


print("\nAll four graphs generated successfully!")
print(f"Output folder: {OUTPUT_DIR}")
print(f"Records analysed: {len(data)}")
