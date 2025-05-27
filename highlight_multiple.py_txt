import re
import sys
import os

# Define different colors for highlighting
COLORS = [
    "\033[43m\033[30m",  # Yellow background, black text
    "\033[44m\033[37m",  # Blue background, white text
    "\033[45m\033[37m",  # Magenta background, white text
    "\033[46m\033[30m",  # Cyan background, black text
    "\033[47m\033[30m",  # White background, black text
]

# Function to highlight multiple keywords with different colors
def highlight_matches(text, keywords):
    # Create a color map for each keyword
    highlighted_text = text
    for i, keyword in enumerate(keywords):
        if i >= len(COLORS):
            print("Warning: More keywords than colors. Using the first color for additional keywords.")
            color_start = COLORS[0]
        else:
            color_start = COLORS[i]
        
        color_end = "\033[0m"  # Reset formatting

        # Case-insensitive search and replace with color
        highlighted_text = re.sub(
            f"({re.escape(keyword)})",
            f"{color_start}\\1{color_end}",
            highlighted_text,
            flags=re.IGNORECASE
        )
    
    return highlighted_text

def main():
    if len(sys.argv) != 3:
        print("Usage: python highlight.py <filename> <keywords>")
        sys.exit(1)

    filename = sys.argv[1]
    keywords_input = sys.argv[2]

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    keywords = keywords_input.split(',')

    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    highlighted = highlight_matches(text, keywords)
    print("\nHighlighted Output:\n")
    print(highlighted)

if __name__ == "__main__":
    main()
