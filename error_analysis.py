
import json
import re
import csv
import unicodedata
from collections import Counter, defaultdict
from jiwer import process_words


# ==========================================
# 1. LOAD REFERENCES AND PREDICTIONS
# ==========================================

with open("references/references.json", "r", encoding="utf-8") as f:
    references = json.load(f)

with open("references/other_speakers.json", "r", encoding="utf-8") as f:
    other_speakers = json.load(f)

with open("results/noisy_transcriptions.json", "r", encoding="utf-8") as f:
    predictions = json.load(f)


# ==========================================
# 2. NORMALIZATION
# ==========================================

REPLACEMENTS = {
    "twelve thousand five hundred fifty rupees": "12550",
    "three thousand two hundred twenty-five rupees": "3225",
    "three thousand two hundred twenty five rupees": "3225",
    "ten thirty": "1030",

    "बारह हजार पाँच सौ पचास रुपये": "12550",
    "बारह हजार पांच सौ पचास रुपये": "12550",
    "तीन हजार दो सौ पच्चीस रुपये": "3225",

    "ट्वेल्व थाउज़ंड फाइव हंड्रेड फिफ्टी रुपीज़": "12550",
    "थ्री थाउज़ंड टू हंड्रेड ट्वेंटी फाइव रुपीज़": "3225",
    "12,500 फ़िफ़्टी रुपये": "12550",
    "12,500 फिफ्टी रुपये": "12550",
    "टेन थर्टी": "1030",

    "12,550": "12550",
    "3,225": "3225",
    "₹": ""
}


def normalize(text):

    text = unicodedata.normalize("NFC", text.lower())

    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    cleaned = ""

    for char in text:
        category = unicodedata.category(char)

        if char.isalnum() or char.isspace() or category.startswith("M"):
            cleaned += char
        else:
            cleaned += " "

    text = re.sub(r"\s+", " ", cleaned).strip()

    text = re.sub(r"\b10\s+30\b", "1030", text)

    return text


# ==========================================
# 3. REFERENCE SELECTION
# ==========================================

def get_reference(speaker_number, language):

    if speaker_number == 1:
        return references[language]

    speaker_key = f"speaker_{speaker_number}"

    return other_speakers[speaker_key][language]


# ==========================================
# 4. STORAGE
# ==========================================

detailed_results = []

substitution_counter = Counter()
deletion_counter = Counter()
insertion_counter = Counter()

language_errors = defaultdict(lambda: [0, 0, 0, 0])
speaker_errors = defaultdict(lambda: [0, 0, 0, 0])

total_hits = 0
total_substitutions = 0
total_deletions = 0
total_insertions = 0
total_reference_words = 0

successful_count = 0
failed_count = 0


print("\n==============================================")
print("       BHARATVOICE BENCH - ERROR ANALYSIS")
print("==============================================\n")


# ==========================================
# 5. PROCESS RECORDINGS
# ==========================================

for item in predictions:

    filename = item.get("file", "unknown")
    status = item.get("status", "unknown")

    match = re.match(
        r"^(english|hindi|hinglish)_(\d+)_(crowd|fan|traffic)_(0|10|20)dB\.wav$",
        filename,
        re.IGNORECASE
    )

    if not match:
        continue

    language = match.group(1).lower()
    speaker_number = int(match.group(2))

    speaker_name = {
        1: "Nandini",
        2: "Shakun",
        3: "Ram"
    }.get(speaker_number, f"Speaker {speaker_number}")

    if status != "success":

        failed_count += 1

        detailed_results.append({
            "file": filename,
            "speaker": speaker_name,
            "language": language,
            "status": "failed",
            "hits": "",
            "substitutions": "",
            "deletions": "",
            "insertions": "",
            "wer_percent": ""
        })

        continue

    try:

        reference = normalize(
            get_reference(speaker_number, language)
        )

        hypothesis = normalize(
            item["response"]["transcript"]
        )

        result = process_words(reference, hypothesis)

        total_hits += result.hits
        total_substitutions += result.substitutions
        total_deletions += result.deletions
        total_insertions += result.insertions

        reference_words = (
            result.hits
            + result.substitutions
            + result.deletions
        )

        total_reference_words += reference_words

        successful_count += 1

        # Store language-wise and speaker-wise counts
        for group in [
            language_errors[language],
            speaker_errors[speaker_name]
        ]:

            group[0] += result.hits
            group[1] += result.substitutions
            group[2] += result.deletions
            group[3] += result.insertions

        # Collect alignment-level error examples
        # jiwer alignment chunks identify substitutions,
        # deletions and insertions.

        ref_words = reference.split()
        hyp_words = hypothesis.split()

        for chunk in result.alignments[0]:

            if chunk.type == "substitute":

                for i in range(chunk.ref_start_idx, chunk.ref_end_idx):
                    ref_word = ref_words[i]

                    hyp_index = (
                        chunk.hyp_start_idx
                        + i - chunk.ref_start_idx
                    )

                    hyp_word = (
                        hyp_words[hyp_index]
                        if hyp_index < chunk.hyp_end_idx
                        else "<missing>"
                    )

                    substitution_counter[
                        (ref_word, hyp_word)
                    ] += 1

            elif chunk.type == "delete":

                for i in range(chunk.ref_start_idx, chunk.ref_end_idx):
                    deletion_counter[ref_words[i]] += 1

            elif chunk.type == "insert":

                for i in range(chunk.hyp_start_idx, chunk.hyp_end_idx):
                    insertion_counter[hyp_words[i]] += 1

        detailed_results.append({
            "file": filename,
            "speaker": speaker_name,
            "language": language,
            "status": "success",
            "hits": result.hits,
            "substitutions": result.substitutions,
            "deletions": result.deletions,
            "insertions": result.insertions,
            "wer_percent": round(result.wer * 100, 2)
        })

    except Exception as e:

        print("Scoring error:", filename, e)


# ==========================================
# 6. OVERALL ERROR SUMMARY
# ==========================================

total_errors = (
    total_substitutions
    + total_deletions
    + total_insertions
)

overall_wer = (
    total_errors / total_reference_words * 100
    if total_reference_words else 0
)

print("\n========== OVERALL ERROR SUMMARY ==========")

print("Successful recordings:", successful_count)
print("Failed recordings:", failed_count)
print("Reference words:", total_reference_words)
print("Correct words:", total_hits)
print("Substitutions:", total_substitutions)
print("Deletions:", total_deletions)
print("Insertions:", total_insertions)
print("Total errors:", total_errors)
print(f"Aggregate WER: {overall_wer:.2f}%")


# ==========================================
# 7. LANGUAGE-WISE ERROR ANALYSIS
# ==========================================

print("\n========== LANGUAGE-WISE ERROR ANALYSIS ==========")

for language, counts in language_errors.items():

    hits, subs, dels, ins = counts

    words = hits + subs + dels
    errors = subs + dels + ins

    wer = errors / words * 100 if words else 0

    print(
        f"{language.upper():<12} "
        f"WER: {wer:.2f}% | "
        f"S: {subs} D: {dels} I: {ins}"
    )


# ==========================================
# 8. SPEAKER-WISE ERROR ANALYSIS
# ==========================================

print("\n========== SPEAKER-WISE ERROR ANALYSIS ==========")

for speaker, counts in speaker_errors.items():

    hits, subs, dels, ins = counts

    words = hits + subs + dels
    errors = subs + dels + ins

    wer = errors / words * 100 if words else 0

    print(
        f"{speaker:<12} "
        f"WER: {wer:.2f}% | "
        f"S: {subs} D: {dels} I: {ins}"
    )


# ==========================================
# 9. MOST FREQUENT SUBSTITUTIONS
# ==========================================

print("\n========== TOP 20 SUBSTITUTIONS ==========")

for (reference_word, predicted_word), count in substitution_counter.most_common(20):

    print(
        f"{reference_word:<20} -> "
        f"{predicted_word:<20} : {count}"
    )


# ==========================================
# 10. MOST FREQUENT DELETIONS
# ==========================================

print("\n========== TOP 20 DELETIONS ==========")

for word, count in deletion_counter.most_common(20):

    print(f"{word:<25} : {count}")


# ==========================================
# 11. MOST FREQUENT INSERTIONS
# ==========================================

print("\n========== TOP 20 INSERTIONS ==========")

for word, count in insertion_counter.most_common(20):

    print(f"{word:<25} : {count}")


# ==========================================
# 12. SAVE DETAILED RECORDING CSV
# ==========================================

with open(
    "results/error_analysis.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    fields = [
        "file",
        "speaker",
        "language",
        "status",
        "hits",
        "substitutions",
        "deletions",
        "insertions",
        "wer_percent"
    ]

    writer = csv.DictWriter(f, fieldnames=fields)

    writer.writeheader()
    writer.writerows(detailed_results)


# ==========================================
# 13. SAVE FREQUENT ERROR CSV
# ==========================================

with open(
    "results/frequent_errors.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    writer.writerow(["error_type", "reference_word", "predicted_word", "frequency"])

    for (ref_word, hyp_word), count in substitution_counter.most_common():

        writer.writerow([
            "substitution",
            ref_word,
            hyp_word,
            count
        ])

    for word, count in deletion_counter.most_common():

        writer.writerow([
            "deletion",
            word,
            "",
            count
        ])

    for word, count in insertion_counter.most_common():

        writer.writerow([
            "insertion",
            "",
            word,
            count
        ])


# ==========================================
# 14. FINAL SUMMARY
# ==========================================

print("\n==============================================")
print("ERROR ANALYSIS COMPLETE")
print("==============================================")

print("Recordings analyzed:", successful_count)
print("Failed recordings:", failed_count)
print("Overall corpus WER:", f"{overall_wer:.2f}%")

print("\nFiles generated:")
print("1. results/error_analysis.csv")
print("2. results/frequent_errors.csv")

print("\nResearch notes:")
print("1. Speaker-specific references were used.")
print("2. Unicode-aware normalization was applied.")
print("3. Failed API requests were excluded from WER.")
print("4. Error types were identified using word alignment.")
print("5. Results describe this experimental dataset only.")

print("==============================================")
