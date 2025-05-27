Here's a **Python Regex Cheat Sheet** to help you quickly reference the most commonly used regex syntax and functionality:

---

## 🔍 **Basic Regex Syntax**

| Pattern  | Matches                                       |                 |        |
| -------- | --------------------------------------------- | --------------- | ------ |
| `.`      | Any character except newline                  |                 |        |
| `^`      | Start of a string                             |                 |        |
| `$`      | End of a string                               |                 |        |
| `*`      | 0 or more repetitions                         |                 |        |
| `+`      | 1 or more repetitions                         |                 |        |
| `?`      | 0 or 1 repetition (also used for non-greedy)  |                 |        |
| `{n}`    | Exactly `n` repetitions                       |                 |        |
| `{n,}`   | `n` or more repetitions                       |                 |        |
| `{n,m}`  | Between `n` and `m` repetitions               |                 |        |
| `[...]`  | Any one of the characters inside the brackets |                 |        |
| `[^...]` | Any character **not** in the brackets         |                 |        |
| \`       | \`                                            | OR (e.g., \`cat | dog\`) |
| `()`     | Group expressions                             |                 |        |
| `\`      | Escape special characters                     |                 |        |

---

## 🆎 **Character Classes**

| Shorthand | Meaning                         |
| --------- | ------------------------------- |
| `\d`      | Digit: `[0-9]`                  |
| `\D`      | Non-digit: `[^0-9]`             |
| `\w`      | Word character: `[a-zA-Z0-9_]`  |
| `\W`      | Non-word character              |
| `\s`      | Whitespace: space, tab, newline |
| `\S`      | Non-whitespace                  |

---

## 🛠 **Regex Functions in Python (`re` module)**

```python
import re

re.match(pattern, string)     # Match only at the beginning
re.search(pattern, string)    # Search anywhere in the string
re.findall(pattern, string)   # Find all matches
re.finditer(pattern, string)  # Returns an iterator of match objects
re.sub(pattern, repl, string) # Substitute
re.split(pattern, string)     # Split string by pattern
```

---

## 📌 **Useful Flags**

| Flag                      | Description                              |
| ------------------------- | ---------------------------------------- |
| `re.IGNORECASE` or `re.I` | Case-insensitive matching                |
| `re.MULTILINE` or `re.M`  | `^` and `$` match start/end of each line |
| `re.DOTALL` or `re.S`     | `.` matches newline as well              |
| `re.VERBOSE` or `re.X`    | Allow multiline regex with comments      |

```python
re.search(r"pattern", text, re.IGNORECASE)
```

---

## 🎯 **Examples**

```python
re.search(r'\d+', 'User123')          # '123'
re.match(r'^Hello', 'Hello World')    # Match at start
re.findall(r'\w+', 'Hi there!')       # ['Hi', 'there']
re.sub(r'\s+', '-', 'a b   c')        # 'a-b-c'
re.split(r'[,;]', 'a,b;c')            # ['a', 'b', 'c']
```

---

## 🔄 **Grouping and Backreferences**

| Syntax           | Description              |
| ---------------- | ------------------------ |
| `(abc)`          | Capturing group          |
| `(?:abc)`        | Non-capturing group      |
| `(?P<name>abc)`  | Named group              |
| `\1`, `\2`, etc. | Backreferences to groups |

---

Would you like a **downloadable version (PDF or markdown)?**
