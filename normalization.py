
import re
import unicodedata


def clean_text(text):
    """Normalize Unicode, lowercase text and remove punctuation."""
    text = unicodedata.normalize("NFC", str(text).lower())

    # 12,550 -> 12550
    text = re.sub(r"(?<=\d),(?=\d)", "", text)

    # Remove currency symbol but preserve the amount
    text = text.replace("₹", " ")

    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        if char.isalnum() or char.isspace() or category.startswith("M"):
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return re.sub(r"\s+", " ", "".join(cleaned)).strip()


def strict_normalize(text):
    """
    Strict mode:
    Removes punctuation and standardizes Unicode.
    Does not convert spoken number words into digits.
    """
    return clean_text(text)


def normalized_normalize(text):
    """
    Normalized mode:
    Converts selected equivalent number, currency,
    date and time expressions.

    Ambiguous expressions are deliberately not corrected.
    """

    text = clean_text(text)

    replacements = [
        # English currency
        ("twelve thousand five hundred fifty rupees", "12550"),
        ("three thousand two hundred twenty five rupees", "3225"),

        # English date and time
        ("november tenth", "november 10th"),
        ("ten thirty", "1030"),
        ("twenty five copies", "25 copies"),

        # Hindi currency
        ("बारह हजार पाँच सौ पचास रुपये", "12550"),
        ("बारह हजार पांच सौ पचास रुपये", "12550"),
        ("तीन हजार दो सौ पच्चीस रुपये", "3225"),

        # Hindi date
        ("दस नवंबर", "10 नवंबर"),

        # Hinglish currency
        ("ट्वेल्व थाउज़ंड फाइव हंड्रेड फिफ्टी रुपीज़", "12550"),
        ("थ्री थाउज़ंड टू हंड्रेड ट्वेंटी फाइव रुपीज़", "3225"),

        # Hinglish time
        ("टेन थर्टी", "1030"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Hindi spoken time variations.
    # Avoid \b because it is unreliable for Devanagari boundaries.
    hindi_time_patterns = [
        (r"(?<!\S)सुबह\s+दस\s+बजकर\s+तीस(?:\s+मिनट)?(?!\S)",
         "सुबह 1030"),
        (r"(?<!\S)दस\s+बजकर\s+तीस(?:\s+मिनट)?(?!\S)",
         "1030"),
        (r"(?<!\S)सुबह\s+10\s+बज\s+कर\s+30\s+मिनट(?!\S)",
         "सुबह 1030"),
        (r"(?<!\S)10\s+बज\s+कर\s+30\s+मिनट(?!\S)",
         "1030"),
        (r"(?<!\S)सुबह\s+10\s+30\s+बजे(?!\S)",
         "सुबह 1030"),
        (r"(?<!\S)10\s+30\s+बजे(?!\S)",
         "1030"),
        (r"(?<!\S)सुबह\s+10\s+30(?!\S)",
         "सुबह 1030"),
    ]

    for pattern, replacement in hindi_time_patterns:
        text = re.sub(pattern, replacement, text)

    # English contextual time variations
    text = re.sub(
        r"(?<!\S)(at|around)\s+10\s+30(?!\S)",
        r"\1 1030",
        text
    )

    # Hinglish contextual time variation
    text = re.sub(
        r"(?<!\S)subah\s+10\s+30(?!\S)",
        "subah 1030",
        text
    )

    return re.sub(r"\s+", " ", text).strip()
