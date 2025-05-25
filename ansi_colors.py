foreground_colors = [
    30, 31, 32, 33, 34, 35, 36, 37, 90, 91, 92, 93, 94, 95, 96, 97
]

background_colors = [
    40, 41, 42, 43, 44, 45, 46, 47, 100, 101, 102, 103, 104, 105, 106, 107
]

# ANSI reset code
reset_code = "\033[0m"

# Function to generate all combinations
def generate_combinations():
    combinations = []
    for fg in foreground_colors:
        for bg in background_colors:
            fg_code = f"\033[{fg}m"
            bg_code = f"\033[{bg}m"
            combination = f"{fg_code}{bg_code}Text{reset_code} (FG: {fg}, BG: {bg})"
            combinations.append(combination)
    return combinations

# Output all combinations
def display_combinations():
    combinations = generate_combinations()
    for combo in combinations:
        print(combo)

if __name__ == "__main__":
    display_combinations()
