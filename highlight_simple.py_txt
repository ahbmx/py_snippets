import re
import sys
import os

def highlight_matches(text, search_term):
    highlight_start = "\033[43m\033[30m"  # Yellow background, black text
    highlight_end = "\033[0m"  # Reset

    highlighted_text = re.sub(
        f"({re.escape(search_term)})",
        f"{highlight_start}\\1{highlight_end}",
        text,
        flags=re.IGNORECASE
    )
    return highlighted_text

def main():
    if len(sys.argv) != 3:
        print("Usage: python highlight.py <filename> <search_term>")
        sys.exit(1)

    filename = sys.argv[1]
    search_term = sys.argv[2]

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    highlighted = highlight_matches(text, search_term)
    print("\nHighlighted Output:\n")
    print(highlighted)

if __name__ == "__main__":
    main()
