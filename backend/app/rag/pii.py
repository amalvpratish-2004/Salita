import re


def mask_pii(text):
    # Mask email addresses
    text = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "[EMAIL]",
        text
    )

    # Mask Indian-style 10 digit phone numbers
    text = re.sub(
        r"\b[6-9]\d{9}\b",
        "[PHONE]",
        text
    )

    return text


if __name__ == "__main__":
    from loader import load_text_file

    file_path = "../../../data/synthetic/pii_example.txt"

    text = load_text_file(file_path)

    print("Original:")
    print(text)

    print("\nAfter PII masking:")
    print(mask_pii(text))