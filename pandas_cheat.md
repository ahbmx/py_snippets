# Python Pandas Cheat Sheet

## Importing Pandas
```python
import pandas as pd
```

## Creating DataFrames
```python
# From dictionary
df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

# From list of lists
df = pd.DataFrame([[1, 'a'], [2, 'b']], columns=['col1', 'col2'])

# From CSV
df = pd.read_csv('file.csv')
```

## Cleaning Column Headers
```python
# Remove special characters and whitespace
df.columns = df.columns.str.replace('[^a-zA-Z0-9]', '_', regex=True)
df.columns = df.columns.str.strip()

# Convert to lowercase
df.columns = df.columns.str.lower()

# Rename specific columns
df = df.rename(columns={'old_name': 'new_name'})
```

## Handling Missing Data
```python
# Drop columns with all NaN values
df = df.dropna(axis=1, how='all')

# Drop rows with any NaN values
df = df.dropna()

# Fill NaN values
df = df.fillna(value)  # with a specific value
df = df.fillna(method='ffill')  # forward fill
df = df.fillna(method='bfill')  # backward fill

# Check for null values
df.isnull().sum()
```

## Selecting Data
```python
# Select column
df['column_name']
df.column_name  # when column name has no spaces/special chars

# Select multiple columns
df[['col1', 'col2']]

# Select rows by index
df.iloc[0]      # first row
df.iloc[0:5]    # first 5 rows
df.iloc[[1,3,5]] # specific rows

# Select rows by condition
df[df['column'] > 10]
df[(df['col1'] > 10) & (df['col2'] == 'value')]
df.query('col1 > 10 and col2 == "value"')

# Select by label
df.loc[row_label, column_label]
```

## Replacing Data
```python
# Replace specific values
df.replace('old_value', 'new_value')
df.replace({'old1': 'new1', 'old2': 'new2'})

# Replace using regex
df.replace({'column': r'pattern'}, {'column': 'replacement'}, regex=True)

# Replace in specific column
df['column'] = df['column'].replace('old', 'new')

# Map values using dictionary
df['column'] = df['column'].map({'val1': 1, 'val2': 2})
```

## DateTime Operations
```python
# Convert string to datetime
df['date_col'] = pd.to_datetime(df['date_col'])

# Extract date components
df['year'] = df['date_col'].dt.year
df['month'] = df['date_col'].dt.month
df['day'] = df['date_col'].dt.day
df['dayofweek'] = df['date_col'].dt.dayofweek  # Monday=0, Sunday=6
df['hour'] = df['date_col'].dt.hour

# Filter by date
df[df['date_col'] > '2023-01-01']
df[(df['date_col'] >= '2023-01-01') & (df['date_col'] <= '2023-01-31')]

# Date arithmetic
df['date_col'] + pd.Timedelta(days=1)
df['date_col'] - pd.Timedelta(hours=3)
df['days_between'] = (df['date_col2'] - df['date_col1']).dt.days
```

## Basic Operations
```python
# Sort values
df.sort_values('column', ascending=False)

# Group by
df.groupby('column')['other_column'].mean()

# Aggregate
df.agg({'col1': 'sum', 'col2': 'mean'})

# Unique values
df['column'].unique()

# Value counts
df['column'].value_counts()

# Apply function
df['column'].apply(lambda x: x*2)
```

## Saving Data
```python
# To CSV
df.to_csv('output.csv', index=False)

# To Excel
df.to_excel('output.xlsx', index=False)
```

## Useful Attributes
```python
df.shape      # (rows, columns)
df.columns    # column names
df.dtypes     # data types
df.index      # index
df.info()     # summary info
df.describe() # statistical summary
```
