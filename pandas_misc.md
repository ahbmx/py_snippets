# Building a Python Package with Pandas Utilities

Here's a comprehensive Python package that provides various pandas utilities for data manipulation. The package includes functions for string operations, date handling, statistical calculations, merging, pivoting, and cross-tabulation.

## Package Structure

```
pandas_utilities/
│
├── __init__.py
├── string_utils.py
├── date_utils.py
├── stats_utils.py
├── merge_utils.py
├── pivot_utils.py
└── crosstab_utils.py
```

## Implementation

### 1. `__init__.py`

```python
"""
Pandas Utilities - A collection of helpful pandas functions for data manipulation.
"""

from .string_utils import *
from .date_utils import *
from .stats_utils import *
from .merge_utils import *
from .pivot_utils import *
from .crosstab_utils import *

__version__ = "0.1.0"
__all__ = [
    # String utilities
    'extract_string_pattern', 'clean_string_columns', 'split_string_column',
    # Date utilities
    'extract_date_parts', 'date_range_filler', 'calculate_date_differences',
    # Stats utilities
    'calculate_zscore', 'winsorize_data', 'calculate_rolling_stats',
    # Merge utilities
    'conditional_join', 'fuzzy_merge',
    # Pivot utilities
    'create_multi_index_pivot', 'flatten_pivot_table',
    # Crosstab utilities
    'percentage_crosstab', 'crosstab_with_margins'
]
```

### 2. `string_utils.py`

```python
import pandas as pd
import re

def extract_string_pattern(df, column, pattern, new_column=None):
    """
    Extract a regex pattern from a string column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column name to extract from
        pattern (str): Regex pattern to extract
        new_column (str): Name for new column (defaults to f"{column}_extracted")
    
    Returns:
        pd.DataFrame: DataFrame with new column containing extracted patterns
    """
    new_col = new_column or f"{column}_extracted"
    df[new_col] = df[column].str.extract(pattern, expand=False)
    return df

def clean_string_columns(df, columns=None, case='lower', strip=True, remove_special=True):
    """
    Clean string columns by adjusting case, stripping whitespace, etc.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (list): List of columns to clean (defaults to all string columns)
        case (str): 'lower', 'upper', or None
        strip (bool): Whether to strip whitespace
        remove_special (bool): Whether to remove special characters
    
    Returns:
        pd.DataFrame: DataFrame with cleaned string columns
    """
    cols = columns or df.select_dtypes(include=['object', 'string']).columns
    
    for col in cols:
        if strip:
            df[col] = df[col].str.strip()
        if case == 'lower':
            df[col] = df[col].str.lower()
        elif case == 'upper':
            df[col] = df[col].str.upper()
        if remove_special:
            df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True)
    
    return df

def split_string_column(df, column, delimiter, new_columns=None, keep_original=False):
    """
    Split a string column into multiple columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column name to split
        delimiter (str): Delimiter to split on
        new_columns (list): Names for new columns
        keep_original (bool): Whether to keep the original column
    
    Returns:
        pd.DataFrame: DataFrame with split columns
    """
    split_df = df[column].str.split(delimiter, expand=True)
    
    if new_columns:
        split_df.columns = new_columns[:split_df.shape[1]]
    else:
        split_df.columns = [f"{column}_{i+1}" for i in range(split_df.shape[1])]
    
    df = pd.concat([df, split_df], axis=1)
    
    if not keep_original:
        df.drop(column, axis=1, inplace=True)
    
    return df
```

### 3. `date_utils.py`

```python
import pandas as pd

def extract_date_parts(df, date_column, parts=None):
    """
    Extract date parts (year, month, day etc.) from a datetime column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_column (str): Name of datetime column
        parts (list): Parts to extract ('year', 'month', 'day', 'weekday', 'hour', etc.)
    
    Returns:
        pd.DataFrame: DataFrame with new columns for each date part
    """
    if parts is None:
        parts = ['year', 'month', 'day']
    
    for part in parts:
        if hasattr(df[date_column].dt, part):
            df[f"{date_column}_{part}"] = getattr(df[date_column].dt, part)
    
    return df

def date_range_filler(df, date_column, freq='D', fill_method=None):
    """
    Ensure a complete date range in the dataframe by filling missing dates.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_column (str): Name of datetime column
        freq (str): Frequency for date range ('D', 'M', 'H', etc.)
        fill_method (str): How to fill missing values ('ffill', 'bfill', etc.)
    
    Returns:
        pd.DataFrame: DataFrame with complete date range
    """
    date_range = pd.date_range(
        start=df[date_column].min(),
        end=df[date_column].max(),
        freq=freq
    )
    
    df = df.set_index(date_column).reindex(date_range)
    
    if fill_method:
        df = df.fillna(method=fill_method)
    
    return df.reset_index().rename(columns={'index': date_column})

def calculate_date_differences(df, date_column1, date_column2, unit='days', new_column=None):
    """
    Calculate differences between two date columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        date_column1 (str): First date column
        date_column2 (str): Second date column
        unit (str): Unit for difference ('days', 'months', 'years', 'hours', etc.)
        new_column (str): Name for new column
    
    Returns:
        pd.DataFrame: DataFrame with new difference column
    """
    new_col = new_column or f"delta_{date_column1}_{date_column2}_{unit}"
    
    delta = df[date_column2] - df[date_column1]
    
    if unit == 'days':
        df[new_col] = delta.dt.days
    elif unit == 'hours':
        df[new_col] = delta.dt.total_seconds() / 3600
    elif unit == 'minutes':
        df[new_col] = delta.dt.total_seconds() / 60
    elif unit == 'months':
        df[new_col] = (df[date_column2].dt.year - df[date_column1].dt.year) * 12 + \
                     (df[date_column2].dt.month - df[date_column1].dt.month)
    elif unit == 'years':
        df[new_col] = df[date_column2].dt.year - df[date_column1].dt.year
    
    return df
```

### 4. `stats_utils.py`

```python
import pandas as pd
import numpy as np
from scipy.stats import zscore

def calculate_zscore(df, columns=None, groupby=None, new_column_suffix='_zscore'):
    """
    Calculate z-scores for numeric columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (list): Columns to calculate z-scores for (defaults to all numeric)
        groupby (str): Column to group by before calculating z-scores
        new_column_suffix (str): Suffix for new z-score columns
    
    Returns:
        pd.DataFrame: DataFrame with new z-score columns
    """
    numeric_cols = columns or df.select_dtypes(include=np.number).columns
    
    if groupby:
        for col in numeric_cols:
            new_col = f"{col}{new_column_suffix}"
            df[new_col] = df.groupby(groupby)[col].transform(
                lambda x: zscore(x, nan_policy='omit')
            )
    else:
        for col in numeric_cols:
            new_col = f"{col}{new_column_suffix}"
            df[new_col] = zscore(df[col], nan_policy='omit')
    
    return df

def winsorize_data(df, columns=None, limits=(0.05, 0.05), groupby=None):
    """
    Winsorize data by capping extreme values at specified percentiles.
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (list): Columns to winsorize (defaults to all numeric)
        limits (tuple): Lower and upper percentile limits
        groupby (str): Column to group by before winsorizing
    
    Returns:
        pd.DataFrame: DataFrame with winsorized columns
    """
    numeric_cols = columns or df.select_dtypes(include=np.number).columns
    
    if groupby:
        for col in numeric_cols:
            def winsorize_group(group):
                lower = group.quantile(limits[0])
                upper = group.quantile(1 - limits[1])
                return group.clip(lower, upper)
            
            df[col] = df.groupby(groupby)[col].transform(winsorize_group)
    else:
        for col in numeric_cols:
            lower = df[col].quantile(limits[0])
            upper = df[col].quantile(1 - limits[1])
            df[col] = df[col].clip(lower, upper)
    
    return df

def calculate_rolling_stats(df, column, window, stats=None, groupby=None):
    """
    Calculate rolling statistics for a column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column to calculate stats for
        window (int): Window size for rolling calculations
        stats (list): Statistics to calculate ('mean', 'median', 'std', 'min', 'max')
        groupby (str): Column to group by before calculating rolling stats
    
    Returns:
        pd.DataFrame: DataFrame with new rolling stat columns
    """
    if stats is None:
        stats = ['mean', 'std']
    
    if groupby:
        for stat in stats:
            new_col = f"{column}_rolling_{window}_{stat}_by_{groupby}"
            df[new_col] = df.groupby(groupby)[column].transform(
                lambda x: x.rolling(window).agg(stat)
            )
    else:
        for stat in stats:
            new_col = f"{column}_rolling_{window}_{stat}"
            df[new_col] = df[column].rolling(window).agg(stat)
    
    return df
```

### 5. `merge_utils.py`

```python
import pandas as pd
from fuzzywuzzy import fuzz

def conditional_join(df1, df2, conditions):
    """
    Perform a conditional join between two dataframes based on multiple conditions.
    
    Args:
        df1 (pd.DataFrame): First dataframe
        df2 (pd.DataFrame): Second dataframe
        conditions (list): List of tuples (col1, col2, operator) where operator is 
                          '==', '>', '<', '>=', '<=', '!='
    
    Returns:
        pd.DataFrame: Merged dataframe based on conditions
    """
    merged = pd.merge(df1, df2, how='cross')
    
    for col1, col2, op in conditions:
        if op == '==':
            merged = merged[merged[col1] == merged[col2]]
        elif op == '>':
            merged = merged[merged[col1] > merged[col2]]
        elif op == '<':
            merged = merged[merged[col1] < merged[col2]]
        elif op == '>=':
            merged = merged[merged[col1] >= merged[col2]]
        elif op == '<=':
            merged = merged[merged[col1] <= merged[col2]]
        elif op == '!=':
            merged = merged[merged[col1] != merged[col2]]
    
    return merged.reset_index(drop=True)

def fuzzy_merge(df1, df2, key1, key2, threshold=90, limit=1):
    """
    Merge dataframes based on fuzzy string matching of columns.
    
    Args:
        df1 (pd.DataFrame): First dataframe
        df2 (pd.DataFrame): Second dataframe
        key1 (str): Key column in first dataframe
        key2 (str): Key column in second dataframe
        threshold (int): Minimum similarity score (0-100)
        limit (int): Maximum number of matches to return per row
    
    Returns:
        pd.DataFrame: Merged dataframe with fuzzy matches
    """
    matches = []
    
    for i, row1 in df1.iterrows():
        scores = []
        for j, row2 in df2.iterrows():
            score = fuzz.token_set_ratio(row1[key1], row2[key2])
            if score >= threshold:
                scores.append((j, score))
        
        # Sort by score descending and take top matches
        scores.sort(key=lambda x: x[1], reverse=True)
        for match in scores[:limit]:
            matches.append((i, match[0], match[1]))
    
    # Create dataframe from matches
    matches_df = pd.DataFrame(matches, columns=['df1_index', 'df2_index', 'match_score'])
    
    # Merge with original dataframes
    result = pd.merge(
        df1.reset_index().rename(columns={'index': 'df1_index'}),
        matches_df,
        on='df1_index'
    )
    result = pd.merge(
        result,
        df2.reset_index().rename(columns={'index': 'df2_index'}),
        on='df2_index'
    )
    
    return result.drop(['df1_index', 'df2_index'], axis=1)
```

### 6. `pivot_utils.py`

```python
import pandas as pd

def create_multi_index_pivot(df, index, columns, values, aggfunc='mean', margins=False):
    """
    Create a pivot table with multi-index columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        index (str/list): Column(s) to use as index
        columns (str/list): Column(s) to use as columns
        values (str/list): Column(s) to aggregate
        aggfunc (str/list/dict): Aggregation function(s)
        margins (bool): Whether to add row/column margins
    
    Returns:
        pd.DataFrame: Pivot table with multi-index columns
    """
    return pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        margins=margins
    )

def flatten_pivot_table(pivot_df, sep='_'):
    """
    Flatten a multi-index pivot table into a single-level column index.
    
    Args:
        pivot_df (pd.DataFrame): Pivot table with multi-index columns
        sep (str): Separator for flattened column names
    
    Returns:
        pd.DataFrame: Flattened dataframe
    """
    pivot_df.columns = [sep.join(map(str, col)).strip() for col in pivot_df.columns.values]
    return pivot_df.reset_index()
```

### 7. `crosstab_utils.py`

```python
import pandas as pd

def percentage_crosstab(df, row, col, normalize='all', margins=False):
    """
    Create a percentage crosstab (contingency table).
    
    Args:
        df (pd.DataFrame): Input dataframe
        row (str): Column for rows
        col (str): Column for columns
        normalize (str): Normalize by 'all', 'index', or 'columns'
        margins (bool): Whether to add row/column margins
    
    Returns:
        pd.DataFrame: Percentage crosstab
    """
    ct = pd.crosstab(
        df[row],
        df[col],
        normalize=normalize,
        margins=margins
    ) * 100
    
    return ct.round(2)

def crosstab_with_margins(df, row, col, values=None, aggfunc='count'):
    """
    Create a crosstab with row and column totals.
    
    Args:
        df (pd.DataFrame): Input dataframe
        row (str): Column for rows
        col (str): Column for columns
        values (str): Column to aggregate (None for count)
        aggfunc (str): Aggregation function
    
    Returns:
        pd.DataFrame: Crosstab with margins
    """
    if values is None:
        ct = pd.crosstab(df[row], df[col], margins=True)
    else:
        ct = pd.crosstab(
            df[row],
            df[col],
            values=df[values],
            aggfunc=aggfunc,
            margins=True
        )
    
    return ct
```

## Setup and Installation

To make this a proper installable package, create a `setup.py` file:

```python
from setuptools import setup, find_packages

setup(
    name="pandas_utilities",
    version="0.1.0",
    description="A collection of useful pandas functions for data manipulation",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy',
        'scipy',
        'fuzzywuzzy',
        'python-Levenshtein'  # For faster fuzzy string matching
    ],
    python_requires='>=3.6',
)
```

## Usage Examples

After installation, users can import and use the functions like this:

```python
from pandas_utilities import (
    clean_string_columns,
    extract_date_parts,
    calculate_zscore,
    fuzzy_merge,
    create_multi_index_pivot,
    percentage_crosstab
)

# Example usage
df = clean_string_columns(df, case='lower')
df = extract_date_parts(df, 'date_column', ['year', 'month'])
df = calculate_zscore(df, columns=['value1', 'value2'])
merged = fuzzy_merge(df1, df2, 'name', 'company', threshold=85)
pivot = create_multi_index_pivot(df, index='category', columns='year', values='sales')
ctab = percentage_crosstab(df, row='gender', col='department')
```

## Documentation

You should also create documentation for your package. Add docstrings to all functions (as shown in the examples) and consider creating a README.md file that explains the package's purpose and provides usage examples.

This package provides a comprehensive set of utilities for common pandas operations, making data manipulation tasks more efficient and consistent.
