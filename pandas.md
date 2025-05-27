# Getting Max Length of Characters in Each Column in Pandas

To find the maximum length of characters in each column of a pandas DataFrame, you can use the following approaches:

## For String Columns Only

```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'A': ['apple', 'banana', 'pear'],
    'B': ['orange', 'kiwi', 'watermelon'],
    'C': [1, 2, 3]
})

# Get max length for string columns
max_lengths = df.select_dtypes(include=['object']).apply(lambda x: x.str.len().max())
print(max_lengths)
```

## For All Columns (Converting Non-String to String First)

```python
# Convert all columns to string and then get lengths
max_lengths = df.astype(str).apply(lambda x: x.str.len().max())
print(max_lengths)
```

## With Column Names for Clarity

```python
max_lengths = df.astype(str).apply(lambda x: x.str.len().max()).rename('max_length')
print(max_lengths)
```

## Handling NaN Values

If your data contains NaN values, you might want to handle them:

```python
max_lengths = df.astype(str).apply(lambda x: x.str.len().replace(np.nan, 0).max())
```

## As a Dictionary

If you prefer the results as a dictionary:

```python
max_length_dict = df.astype(str).apply(lambda x: x.str.len().max()).to_dict()
```

These methods will give you the maximum number of characters in each column of your DataFrame.
