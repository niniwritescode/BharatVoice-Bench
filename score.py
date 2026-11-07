
import json
import re
import csv
import unicodedata
from jiwer import process_words


# ==================================================
# 1. LOAD REFERENCE TRANSCRIPTS
# ==================================================

with open("references/references.json", "r", encoding="utf-8") as f:
    references_1 = json.load(f)

with open("references/other_speakers.json", "r", encoding="utf-8") as f:
    other_references = json.load(f)


# ==================================================
# 2. LOAD GNANI API PREDICTIONS
# ==================================================

with open("results/transcriptions.json", "r", encoding="utf-8") as f:
    predictions = json.load(f)


# ==================================================
# 3. COMBINE ALL NINE REFERENCE TRANSCRIPTS
# ==================================================

tests = {
    "english": references_1["english"],
    "hindi": references_1["hindi"],
    "hinglish": references_1["hinglish"],

    "speaker_2_english": other_references["speaker_2"]["english"],
    "speaker_2_hindi": other_references["speaker_2"]["hindi"],
    "speaker_2_hinglish": other_references["speaker_2"]["hinglish"],

    "speaker_3_english": other_references["speaker_3"]["english"],
    "speaker_3_hindi": other_references["speaker_3"]["hindi"],
    "speaker_3_hinglish": other_references["speaker_3"]["hinglish"],
}


# ==================================================
# 4. TEXT NORMALIZATION
# ==================================================

def normalize(text):

    text = unicodedata.normalize("NFC", text.lower())

    # Remove commas inside numbers: 12,550 -> 12550
    text = re.sub(r"(?<=\d),(?=\d)", "", text)

    # Remove punctuation while preserving Hindi vowel marks
    cleaned = ""

    for char in text:
        category = unicodedata.category(char)

        if category.startswith(("L", "N", "M")) or char.isspace():
            cleaned += char
        else:
            cleaned += " "

    text = re.sub(r"\s+", " ", cleaned).strip()

    # Equivalent number and time expressions
    replacements = {

        # English
        "twelve thousand five hundred fifty rupees": "12550",
        "three thousand two hundred twenty five rupees": "3225",
        "twelve thousand five hundred fifty": "12550",
        "three thousand two hundred twenty five": "3225",
        "twenty five": "25",
        "ten thirty": "1030",
        "november tenth": "november 10th",

        # Hindi
        "बारह हजार पाँच सौ पचास रुपये": "12550",
        "तीन हजार दो सौ पच्चीस रुपये": "3225",
        "बारह हजार पाँच सौ पचास": "12550",
        "तीन हजार दो सौ पच्चीस": "3225",
        "दस बजकर तीस मिनट": "1030",

        # Hinglish
        "ट्वेल्व थाउज़ंड फाइव हंड्रेड फिफ्टी रुपीज़": "12550",
        "थ्री थाउज़ंड टू हंड्रेड ट्वेंटी फाइव रुपीज़": "3225",
        "ट्वेल्व थाउज़ंड फाइव हंड्रेड फिफ्टी": "12550",
        "थ्री थाउज़ंड टू हंड्रेड ट्वेंटी फाइव": "3225",
        "टेन थर्टी": "1030",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize the Hinglish number split in ASR output
    text = re.sub(
        r"\b12500\s+फ़िफ़्टी\b",
        "12550",
        text
    )

    # Normalize time formatting: 10 30 -> 1030
    text = re.sub(r"\b10\s+30\b", "1030", text)

    return re.sub(r"\s+", " ", text).strip()


# ==================================================
# 5. SCORE ALL NINE RECORDINGS
# ==================================================

print("\n========== BHARATVOICE BENCH ==========")
print("          CLEAN BASELINE WER")
print("=======================================\n")

csv_rows = []

language_totals = {
    "english": [0, 0, 0, 0, 0],
    "hindi": [0, 0, 0, 0, 0],
    "hinglish": [0, 0, 0, 0, 0]
}

# Totals: words, hits, substitutions, deletions, insertions

for name, reference_text in tests.items():

    if name not in predictions:
        print(f"SKIPPED: {name} - prediction not found")
        continue

    hypothesis_text = predictions[name].get("transcript")

    if not hypothesis_text:
        print(f"SKIPPED: {name} - transcript missing")
        continue

    reference = normalize(reference_text)
    hypothesis = normalize(hypothesis_text)

    result = process_words(reference, hypothesis)

    words = (
        result.hits
        + result.substitutions
        + result.deletions
    )

    errors = (
        result.substitutions
        + result.deletions
        + result.insertions
    )

    wer = errors / words if words else 0

    print(f"\n{name.upper()}")
    print("-" * 45)
    print(f"Reference words : {words}")
    print(f"Correct matches : {result.hits}")
    print(f"Substitutions   : {result.substitutions}")
    print(f"Deletions       : {result.deletions}")
    print(f"Insertions      : {result.insertions}")
    print(f"WER             : {wer:.2%}")

    csv_rows.append({
        "recording": name,
        "reference_words": words,
        "hits": result.hits,
        "substitutions": result.substitutions,
        "deletions": result.deletions,
        "insertions": result.insertions,
        "WER_percent": round(wer * 100, 2)
    })

    # Determine language from recording name
    language = name.split("_")[-1]

    totals = language_totals[language]

    totals[0] += words
    totals[1] += result.hits
    totals[2] += result.substitutions
    totals[3] += result.deletions
    totals[4] += result.insertions


# ==================================================
# 6. LANGUAGE-WISE AGGREGATE WER
# ==================================================

print("\n\n========== LANGUAGE-WISE RESULTS ==========")

for language, totals in language_totals.items():

    words, hits, subs, dels, ins = totals

    if words == 0:
        continue

    total_errors = subs + dels + ins
    wer = total_errors / words

    print(f"\n{language.upper()}")
    print("-" * 40)
    print(f"Total reference words: {words}")
    print(f"Correct matches: {hits}")
    print(f"Substitutions: {subs}")
    print(f"Deletions: {dels}")
    print(f"Insertions: {ins}")
    print(f"Aggregate WER: {wer:.2%}")


# ==================================================
# 7. SAVE INDIVIDUAL RESULTS TO CSV
# ==================================================

with open(
    "results/clean_wer_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as f:

    fieldnames = [
        "recording",
        "reference_words",
        "hits",
        "substitutions",
        "deletions",
        "insertions",
        "WER_percent"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(csv_rows)


# ==================================================
# 8. COMPLETION MESSAGE
# ==================================================

print("\n=======================================")
print("CLEAN BASELINE SCORING COMPLETED!")
print("Total recordings scored:", len(csv_rows))
print("Results saved to:")
print("results/clean_wer_results.csv")
print("=======================================")
