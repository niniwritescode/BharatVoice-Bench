import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SOURCE = BASE_DIR / "results" / "noisy_wer_normalized.csv"
OUTPUT_DIR = BASE_DIR / "public_data"
OUTPUT = OUTPUT_DIR / "noisy_wer_summary.csv"

# Only these fields are allowed in the public dataset.
PUBLIC_FIELDS = [
    "file",
    "speaker",
    "language",
    "noise",
    "snr",
    "wer",
    "substitutions",
    "deletions",
    "insertions",
    "reference_words",
]

if not SOURCE.exists():
    raise FileNotFoundError(
        f"Private source dataset not found: {SOURCE}"
    )

OUTPUT_DIR.mkdir(exist_ok=True)

speaker_map = {}
exported_rows = []

with open(SOURCE, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    for index, row in enumerate(reader, start=1):
        original_speaker = row.get("speaker", "Unknown")

        if original_speaker not in speaker_map:
            speaker_map[original_speaker] = (
                f"Speaker {len(speaker_map) + 1}"
            )

        exported_rows.append({
            "file": f"record_{index:03d}",
            "speaker": speaker_map[original_speaker],
            "language": row.get("language", ""),
            "noise": row.get("noise", ""),
            "snr": row.get("snr", ""),
            "wer": row.get("wer", ""),
            "substitutions": row.get("substitutions", ""),
            "deletions": row.get("deletions", ""),
            "insertions": row.get("insertions", ""),
            "reference_words": row.get("reference_words", ""),
        })

with open(OUTPUT, "w", encoding="utf-8", newline="") as destination:
    writer = csv.DictWriter(
        destination,
        fieldnames=PUBLIC_FIELDS
    )
    writer.writeheader()
    writer.writerows(exported_rows)

print("Public dataset created successfully.")
print(f"Records exported: {len(exported_rows)}")
print(f"Speakers anonymized: {len(speaker_map)}")
print(f"Output: {OUTPUT}")