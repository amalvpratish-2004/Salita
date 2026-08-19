import re


def clean_text(text):
    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning/end of lines
    lines = text.splitlines()
    lines = [line.strip() for line in lines]

    # Remove empty lines at the beginning/end
    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    return "\n".join(lines)


if __name__ == "__main__":
    from loader import load_text_file

    file_path = "../../../data/synthetic/loan_eligibility.txt"

    raw_text = load_text_file(file_path)
    clean = clean_text(raw_text)

    print("Cleaning completed!")
    print("Original characters:", len(raw_text))
    print("Cleaned characters:", len(clean))
    print()
    print(clean)