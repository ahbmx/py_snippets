# Converting Different Data Structures to Pandas DataFrame in Python

Here are examples of converting various Python data structures to pandas DataFrames:

## 1. From Dictionary

```python
import pandas as pd

# Dictionary where keys become column names
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'London', 'Paris']
}

df = pd.DataFrame(data)
print(df)
```

## 2. From List of Dictionaries

```python
data = [
    {'Name': 'Alice', 'Age': 25, 'City': 'New York'},
    {'Name': 'Bob', 'Age': 30, 'City': 'London'},
    {'Name': 'Charlie', 'Age': 35, 'City': 'Paris'}
]

df = pd.DataFrame(data)
print(df)
```

## 3. From List of Lists (with column names)

```python
data = [
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'London'],
    ['Charlie', 35, 'Paris']
]

columns = ['Name', 'Age', 'City']
df = pd.DataFrame(data, columns=columns)
print(df)
```

## 4. From NumPy Array

```python
import numpy as np

arr = np.array([
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'London'],
    ['Charlie', 35, 'Paris']
])

df = pd.DataFrame(arr, columns=['Name', 'Age', 'City'])
print(df)
```

## 5. From CSV File

```python
df = pd.read_csv('data.csv')  # Reads CSV into DataFrame
print(df)
```

## 6. From JSON

```python
json_data = '''
[
    {"Name": "Alice", "Age": 25, "City": "New York"},
    {"Name": "Bob", "Age": 30, "City": "London"},
    {"Name": "Charlie", "Age": 35, "City": "Paris"}
]
'''

df = pd.read_json(json_data)
print(df)
```

## 7. From SQL Database

```python
import sqlite3

conn = sqlite3.connect('example.db')
df = pd.read_sql('SELECT * FROM users', conn)
conn.close()
print(df)
```

## 8. From Excel File

```python
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
print(df)
```

## 9. From Series

```python
names = pd.Series(['Alice', 'Bob', 'Charlie'])
ages = pd.Series([25, 30, 35])

df = pd.DataFrame({'Name': names, 'Age': ages})
print(df)
```

## 10. From Dictionary with Different Lengths

```python
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30],  # Shorter length
    'City': ['New York', 'London', 'Paris', 'Tokyo']  # Longer length
}

df = pd.DataFrame.from_dict(data, orient='index').transpose()
print(df)
```

These examples cover most common data structures you might need to convert to pandas DataFrames. The DataFrame constructor is flexible and can handle many different input formats.
