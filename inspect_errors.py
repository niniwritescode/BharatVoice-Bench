
import csv
import json
import re
from normalization import strict_normalize, normalized_normalize
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

STRICT_OUTPUT = RESULTS_DIR / "error_inspection_strict.csv"
NORMALIZED_OUTPUT = RESULTS_DIR / "error_inspection_normalized.csv"


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
# 4. GET REFERENCE
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
# 7. CHECK SUCCESS
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
# 8. INSPECT ALIGNMENT ERRORS
# ==================================================

def inspect_recording(
    reference,
    hypothesis,
    normalizer,
    mode,
    details,
    filename
):

    normalized_reference = normalizer(reference)
    normalized_hypothesis = normalizer(hypothesis)

    result = process_words(
        normalized_reference,
        normalized_hypothesis
    )

    error_rows = []

    reference_words = normalized_reference.split()
    hypothesis_words = normalized_hypothesis.split()

    for sentence_alignment in result.alignments:

        for chunk in sentence_alignment:

            if chunk.type == "equal":
                continue

            ref_text = " ".join(
                reference_words[
                    chunk.ref_start_idx:chunk.ref_end_idx
                ]
            )

            hyp_text = " ".join(
                hypothesis_words[
                    chunk.hyp_start_idx:chunk.hyp_end_idx
                ]
            )

            error_rows.append({

                "file": filename,
                "speaker": details["speaker"],
                "language": details["language"],
                "noise": details["noise"],
                "snr": details["snr"],
                "mode": mode,
                "error_type": chunk.type,
                "reference": ref_text,
                "hypothesis": hyp_text,

            })

    return result, error_rows


# ==================================================
# 9. PROCESS RECORDINGS
# ==================================================

strict_errors = []
normalized_errors = []

strict_files_with_errors = set()
normalized_files_with_errors = set()

failed_files = []
unexpected_files = []

for item in transcription_data:

    filename = item.get("file", "")

    details = get_file_details(filename)

    if not details:
        unexpected_files.append(filename)
        continue

    if not is_successful(item):
        failed_files.append(filename)
        continue

    hypothesis = extract_transcript(
        item.get("response", {})
    )

    if not hypothesis:
        failed_files.append(filename)
        continue

    try:

        reference = get_reference(
            details["speaker_number"],
            details["language"]
        )

        # ------------------------------------------
        # STRICT INSPECTION
        # ------------------------------------------

        strict_result, strict_rows = inspect_recording(
            reference,
            hypothesis,
            strict_normalize,
            "strict",
            details,
            filename
        )

        strict_errors.extend(strict_rows)

        if strict_rows:
            strict_files_with_errors.add(filename)

        # ------------------------------------------
        # NORMALIZED INSPECTION
        # ------------------------------------------

        normalized_result, normalized_rows = inspect_recording(
            reference,
            hypothesis,
            normalized_normalize,
            "normalized",
            details,
            filename
        )

        normalized_errors.extend(normalized_rows)

        if normalized_rows:
            normalized_files_with_errors.add(filename)

    except Exception as error:

        print(
            f"Could not inspect {filename}: {error}"
        )


# ==================================================
# 10. SAVE CSV FILES
# ==================================================

CSV_FIELDS = [
    "file",
    "speaker",
    "language",
    "noise",
    "snr",
    "mode",
    "error_type",
    "reference",
    "hypothesis",
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


save_csv(STRICT_OUTPUT, strict_errors)
save_csv(NORMALIZED_OUTPUT, normalized_errors)


# ==================================================
# 11. SUMMARY
# ==================================================

print("\n" + "=" * 65)
print("ERROR INSPECTION SUMMARY")
print("=" * 65)

print(f"Total input entries         : {len(transcription_data)}")
print(f"Failed / skipped recordings : {len(failed_files)}")
print(f"Unexpected filenames        : {len(unexpected_files)}")

print("\nSTRICT MODE")

print(
    f"Files containing errors     : "
    f"{len(strict_files_with_errors)}"
)

print(
    f"Total error chunks          : "
    f"{len(strict_errors)}"
)

print("\nNORMALIZED MODE")

print(
    f"Files containing errors     : "
    f"{len(normalized_files_with_errors)}"
)

print(
    f"Total error chunks          : "
    f"{len(normalized_errors)}"
)

print("\nCSV FILES SAVED:")

print(STRICT_OUTPUT)
print(NORMALIZED_OUTPUT)


# ==================================================
# 12. DISPLAY NORMALIZED ERROR EXAMPLES
# ==================================================

print("\n" + "=" * 65)
print("NORMALIZED ERROR EXAMPLES")
print("=" * 65)

for row in normalized_errors[:30]:

    print(f"\nFile       : {row['file']}")
    print(f"Speaker    : {row['speaker']}")
    print(f"Language   : {row['language']}")
    print(f"Noise      : {row['noise']} at {row['snr']}")
    print(f"Error type : {row['error_type']}")
    print(f"Reference  : {row['reference']}")
    print(f"ASR output : {row['hypothesis']}")

if len(normalized_errors) > 30:

    print(
        f"\n...and {len(normalized_errors) - 30} more error chunks."
    )

    print(
        "Open error_inspection_normalized.csv "
        "to view all errors."
    )
