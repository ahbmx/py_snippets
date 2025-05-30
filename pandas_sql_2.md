# Enhanced Python Function to Create dtypes Dictionary for DataFrame

Here's an enhanced version that includes a function to create a dtypes dictionary for the DataFrame, which can be useful for specifying data types when reading data:

```python
import pandas as pd
import numpy as np

def get_dataframe_dtypes(df):
    """
    Create a dtypes dictionary that can be used to specify column types when reading data.
    This preserves the original data types before any automatic type inference.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame
    
    Returns:
    dict: A dictionary mapping column names to pandas/numpy dtypes
    """
    dtypes_dict = {}
    for column in df.columns:
        dtype = df[column].dtype
        # Convert to numpy dtype for consistency
        numpy_dtype = np.dtype(dtype)
        dtypes_dict[column] = numpy_dtype
    
    return dtypes_dict

def get_mysql_schema(df):
    """
    Analyze a pandas DataFrame and generate MySQL schema information including:
    - Recommended MySQL data types
    - Maximum lengths for string columns
    - Nullability information
    
    Parameters:
    df (pd.DataFrame): Input DataFrame to analyze
    
    Returns:
    dict: A dictionary containing column information suitable for MySQL schema creation
    """
    
    type_mapping = {
        'int64': 'INT',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'DATETIME',
        'timedelta64[ns]': 'TIME',
        'object': 'VARCHAR',
        'category': 'VARCHAR'
    }
    
    schema_info = {}
    
    for column in df.columns:
        col_info = {}
        dtype = str(df[column].dtype)
        
        # Determine MySQL data type
        mysql_type = type_mapping.get(dtype, 'VARCHAR')
        
        # Handle string/object columns
        if dtype == 'object' or dtype == 'category':
            # Calculate max length
            max_length = df[column].astype(str).str.len().max()
            
            # Add buffer (20% or minimum 10 characters)
            buffer = max(int(max_length * 1.2), max_length + 10)
            col_info['type'] = f'VARCHAR({min(buffer, 65535)})'  # MySQL VARCHAR max is 65,535
            
            # Check if it might be better as TEXT for very long strings
            if buffer > 255:  # Common threshold for considering TEXT
                col_info['type'] = 'TEXT'
        
        # Handle integer columns
        elif 'int' in dtype:
            col_min = df[column].min()
            col_max = df[column].max()
            
            # Determine appropriate integer type
            if col_min >= 0:  # Unsigned
                if col_max < 256:
                    col_info['type'] = 'TINYINT UNSIGNED'
                elif col_max < 65536:
                    col_info['type'] = 'SMALLINT UNSIGNED'
                elif col_max < 16777216:
                    col_info['type'] = 'MEDIUMINT UNSIGNED'
                elif col_max < 4294967296:
                    col_info['type'] = 'INT UNSIGNED'
                else:
                    col_info['type'] = 'BIGINT UNSIGNED'
            else:  # Signed
                if col_min >= -128 and col_max <= 127:
                    col_info['type'] = 'TINYINT'
                elif col_min >= -32768 and col_max <= 32767:
                    col_info['type'] = 'SMALLINT'
                elif col_min >= -8388608 and col_max <= 8388607:
                    col_info['type'] = 'MEDIUMINT'
                elif col_min >= -2147483648 and col_max <= 2147483647:
                    col_info['type'] = 'INT'
                else:
                    col_info['type'] = 'BIGINT'
        
        # Handle float/double
        elif 'float' in dtype:
            # Check if values are actually decimals (fixed precision)
            if df[column].apply(lambda x: isinstance(x, float)) and not df[column].isnull().all():
                # Count decimal places
                decimal_places = df[column].astype(str).str.extract(r'\.(\d+)')[0].str.len().max()
                if pd.notna(decimal_places) and decimal_places > 0:
                    # Estimate total digits
                    total_digits = len(str(int(df[column].abs().max()))) + decimal_places
                    col_info['type'] = f'DECIMAL({total_digits},{decimal_places})'
                else:
                    col_info['type'] = 'FLOAT'
            else:
                col_info['type'] = 'FLOAT'
        
        # Handle datetime
        elif 'datetime' in dtype:
            col_info['type'] = 'DATETIME'
        
        # Handle boolean
        elif 'bool' in dtype:
            col_info['type'] = 'BOOLEAN'
        
        # Default to VARCHAR if type not recognized
        else:
            col_info['type'] = 'VARCHAR(255)'
        
        # Determine nullability
        col_info['nullable'] = df[column].isnull().any()
        
        # Add original pandas dtype
        col_info['pandas_dtype'] = str(df[column].dtype)
        
        # Add to schema info
        schema_info[column] = col_info
    
    return schema_info

def generate_mysql_create_table(df, table_name):
    """
    Generate a MySQL CREATE TABLE statement based on DataFrame analysis
    
    Parameters:
    df (pd.DataFrame): Input DataFrame
    table_name (str): Name for the MySQL table
    
    Returns:
    str: CREATE TABLE statement
    """
    schema = get_mysql_schema(df)
    
    columns = []
    for col_name, col_info in schema.items():
        col_def = f"`{col_name}` {col_info['type']}"
        if not col_info['nullable']:
            col_def += " NOT NULL"
        columns.append(col_def)
    
    create_table = f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(columns)
    create_table += "\n);"
    
    return create_table
```

## Usage Examples

### 1. Getting DataFrame dtypes dictionary

```python
# Create a sample DataFrame
data = {
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'price': [10.99, 20.50, 15.75],
    'is_active': [True, False, True],
    'created_at': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
}

df = pd.DataFrame(data)

# Get dtypes dictionary
dtypes_dict = get_dataframe_dtypes(df)
print("DataFrame dtypes dictionary:")
print(dtypes_dict)
```

### 2. Using the dtypes dictionary when reading data

```python
# Example of using the dtypes dictionary when reading a CSV
dtypes_dict = {
    'id': np.int64,
    'name': object,
    'age': np.int64,
    'price': np.float64,
    'is_active': bool,
    'created_at': np.datetime64
}

# You can use it like this when reading data:
# df = pd.read_csv('data.csv', dtype=dtypes_dict, parse_dates=['created_at'])
```

### 3. Full workflow example

```python
# Full workflow example
data = {
    'product_id': [101, 102, 103],
    'product_name': ['Laptop', 'Phone', 'Tablet'],
    'price': [999.99, 699.50, 329.99],
    'in_stock': [True, False, True],
    'launch_date': pd.to_datetime(['2022-01-15', '2022-03-20', '2022-05-10']),
    'description': ['High performance laptop', 'Latest smartphone model', 'Portable tablet device']
}

df = pd.DataFrame(data)

# 1. Get the dtypes dictionary
dtypes_dict = get_dataframe_dtypes(df)
print("Data Types Dictionary:")
print(dtypes_dict)

# 2. Get MySQL schema information
schema_info = get_mysql_schema(df)
print("\nMySQL Schema Information:")
for col, info in schema_info.items():
    print(f"{col}: {info}")

# 3. Generate CREATE TABLE statement
create_table = generate_mysql_create_table(df, 'products')
print("\nCREATE TABLE Statement:")
print(create_table)
```

## Key Enhancements:

1. **New `get_dataframe_dtypes` function**:
   - Creates a dictionary mapping column names to their pandas/numpy dtypes
   - Useful for preserving original data types when reading data
   - Helps maintain consistency in data type handling

2. **Additional metadata in schema info**:
   - Added original pandas dtype to the MySQL schema information
   - Helps with debugging and understanding type conversions

3. **Improved documentation**:
   - Clearer usage examples showing the full workflow
   - Better explanation of how to use the dtypes dictionary

This enhanced version provides a complete solution for both analyzing your existing DataFrame's data types and using that information to create appropriate MySQL schemas.
