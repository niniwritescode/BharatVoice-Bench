
import csv
import json
import re
from normalization import strict_normalize, normalized_normalize
from collections import defaultdict
from pathlib import Path

from jiwer import process_words


# ==================================================
# 1. PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

REFERENCES_DIR = BASE_DIR / "references"
RESULTS_DIR = BASE_DIR / "results"

REFERENCE_FILE = REFERENCES_DIR / "references.json"
OTHER_SPEAKERS_FILE = REFERENCES_DIR / "other_speakers.json"
TRANSCRIPTIONS_FILE = RESULTS_DIR / "noisy_transcriptions.json"

STRICT_OUTPUT = RESULTS_DIR / "noisy_wer_strict.csv"
NORMALIZED_OUTPUT = RESULTS_DIR / "noisy_wer_normalized.csv"

RESULTS_DIR.mkdir(exist_ok=True)


# ==================================================
# 2. LOAD DATA
# ==================================================

with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
    references = json.load(f)

with open(OTHER_SPEAKERS_FILE, "r", encoding="utf-8") as f:
    other_speakers = json.load(f)

with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
    transcription_data = json.load(f)


# ==================================================
# 3. EXTRACT TRANSCRIPT
# ==================================================

def extract_transcript(value):

    preferred_keys = (
        "transcript",
        "transcription",
        "text",
        "recognized_text",
        "recognised_text",
        "result",
    )

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):

        for key in preferred_keys:
            if key in value:
                result = extract_transcript(value[key])

                if result:
                    return result

        for nested_value in value.values():
            result = extract_transcript(nested_value)

            if result:
                return result

    if isinstance(value, list):

        for item in value:
            result = extract_transcript(item)

            if result:
                return result

    return ""


# ==================================================
# 4. GET CORRECT REFERENCE
# ==================================================

def get_reference(speaker_number, language):

    if speaker_number == "01":
        return references[language]

    speaker_key = f"speaker_{int(speaker_number)}"

    return other_speakers[speaker_key][language]



# ==================================================
# 6. FILENAME INFORMATION
# ==================================================

FILENAME_PATTERN = re.compile(
    r"^(english|hindi|hinglish)_(\d+)_(crowd|fan|traffic)_(0|10|20)dB\.wav$",
    re.IGNORECASE
)


def get_file_details(filename):

    match = FILENAME_PATTERN.match(filename)

    if not match:
        return None

    language, speaker_number, noise_type, snr = match.groups()

    speaker_names = {
        "01": "Nandini",
        "02": "Shakun",
        "03": "Ram",
    }

    return {
        "language": language.lower(),
        "speaker_number": speaker_number,
        "speaker": speaker_names.get(
            speaker_number,
            f"Speaker {speaker_number}"
        ),
        "noise": noise_type.lower(),
        "snr": f"{snr}dB",
    }


# ==================================================
# 7. CHECK API SUCCESS
# ==================================================

def is_successful(item):

    if item.get("error"):
        return False

    status = item.get("status")

    if status is None:
        return bool(extract_transcript(item.get("response", {})))

    if isinstance(status, int):
        return 200 <= status < 300

    status_text = str(status).strip().lower()

    if status_text in (
        "success",
        "successful",
        "ok",
        "200",
        "true"
    ):
        return True

    if status_text in (
        "failed",
        "failure",
        "error",
        "false"
    ):
        return False

    return bool(extract_transcript(item.get("response", {})))


# ==================================================
# 8. CALCULATE WER
# ==================================================

def calculate_wer(reference, hypothesis, normalizer):

    normalized_reference = normalizer(reference)
    normalized_hypothesis = normalizer(hypothesis)

    result = process_words(
        normalized_reference,
        normalized_hypothesis
    )

    reference_words = (
        result.hits
        + result.substitutions
        + result.deletions
    )

    return {
        "reference": normalized_reference,
        "hypothesis": normalized_hypothesis,
        "wer": result.wer * 100,
        "hits": result.hits,
        "substitutions": result.substitutions,
        "deletions": result.deletions,
        "insertions": result.insertions,
        "reference_words": reference_words,
    }


def calculate_totals(rows):

    hits = sum(row["hits"] for row in rows)
    substitutions = sum(row["substitutions"] for row in rows)
    deletions = sum(row["deletions"] for row in rows)
    insertions = sum(row["insertions"] for row in rows)
    reference_words = sum(row["reference_words"] for row in rows)

    errors = substitutions + deletions + insertions

    wer = (
        errors / reference_words * 100
        if reference_words
        else 0
    )

    return {
        "recordings": len(rows),
        "hits": hits,
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "reference_words": reference_words,
        "wer": wer,
    }


# ==================================================
# 9. PROCESS ALL RECORDINGS
# ==================================================

strict_rows = []
normalized_rows = []

failed_files = []
unexpected_files = []

for item in transcription_data:

    filename = item.get("file", "")

    details = get_file_details(filename)

    if not details:
        unexpected_files.append(filename)
        continue

    if not is_successful(item):

        failed_files.append({
            "file": filename,
            "error": item.get("error", "No successful transcript"),
            "http_status": item.get("http_status", ""),
        })

        continue

    hypothesis = extract_transcript(
        item.get("response", {})
    )

    if not hypothesis:

        failed_files.append({
            "file": filename,
            "error": "Transcript could not be extracted",
            "http_status": item.get("http_status", ""),
        })

        continue

    try:

        reference = get_reference(
            details["speaker_number"],
            details["language"]
        )

        strict_result = calculate_wer(
            reference,
            hypothesis,
            strict_normalize
        )

        normalized_result = calculate_wer(
            reference,
            hypothesis,
            normalized_normalize
        )

        common_data = {
            "file": filename,
            "speaker": details["speaker"],
            "language": details["language"],
            "noise": details["noise"],
            "snr": details["snr"],
            "reference_original": reference,
            "transcript_original": hypothesis,
        }

        strict_rows.append({
            **common_data,
            **strict_result,
        })

        normalized_rows.append({
            **common_data,
            **normalized_result,
        })

    except Exception as error:

        failed_files.append({
            "file": filename,
            "error": f"Scoring error: {error}",
            "http_status": item.get("http_status", ""),
        })


# ==================================================
# 10. SAVE CSV
# ==================================================

CSV_FIELDS = [
    "file",
    "speaker",
    "language",
    "noise",
    "snr",
    "reference_original",
    "transcript_original",
    "reference",
    "hypothesis",
    "wer",
    "hits",
    "substitutions",
    "deletions",
    "insertions",
    "reference_words",
]


def save_csv(path, rows):

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


save_csv(STRICT_OUTPUT, strict_rows)
save_csv(NORMALIZED_OUTPUT, normalized_rows)


# ==================================================
# 11. GROUP REPORT
# ==================================================

def print_group_report(title, rows, group_key):

    groups = defaultdict(list)

    for row in rows:
        groups[row[group_key]].append(row)

    print(f"\n{title}")

    for group_name in sorted(groups):

        totals = calculate_totals(groups[group_name])

        print(
            f"{group_name:<12} "
            f"WER: {totals['wer']:.2f}% | "
            f"Recordings: {totals['recordings']} | "
            f"S: {totals['substitutions']} "
            f"D: {totals['deletions']} "
            f"I: {totals['insertions']}"
        )


def print_report(title, rows):

    totals = calculate_totals(rows)

    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    print(f"Successful recordings : {totals['recordings']}")
    print(f"Reference words       : {totals['reference_words']}")
    print(f"Correct words (hits)  : {totals['hits']}")
    print(f"Substitutions         : {totals['substitutions']}")
    print(f"Deletions             : {totals['deletions']}")
    print(f"Insertions            : {totals['insertions']}")
    print(f"Overall corpus WER    : {totals['wer']:.2f}%")

    print_group_report("BY LANGUAGE", rows, "language")
    print_group_report("BY NOISE TYPE", rows, "noise")
    print_group_report("BY SNR", rows, "snr")
    print_group_report("BY SPEAKER", rows, "speaker")


# ==================================================
# 12. FINAL REPORT
# ==================================================

print_report(
    "STRICT WER RESULTS",
    strict_rows
)

print_report(
    "NORMALIZED WER RESULTS",
    normalized_rows
)

print("\n" + "=" * 65)
print("DATASET CHECK")
print("=" * 65)

print(f"Total input entries       : {len(transcription_data)}")
print(f"Successfully scored       : {len(strict_rows)}")
print(f"Failed / unscored entries : {len(failed_files)}")
print(f"Unexpected filenames     : {len(unexpected_files)}")

if failed_files:

    print("\nFAILED FILES:")

    for failed in failed_files:

        print(
            f"- {failed['file']} | "
            f"{failed['error']} | "
            f"HTTP: {failed['http_status']}"
        )

if unexpected_files:

    print("\nUNRECOGNIZED FILENAMES:")

    for filename in unexpected_files:
        print(f"- {filename}")

print("\nCSV FILES SAVED:")
print(STRICT_OUTPUT)
print(NORMALIZED_OUTPUT)
