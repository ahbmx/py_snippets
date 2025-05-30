# Python Function to Identify Dtypes and Calculate Max Length for MySQL

Here's a Python function that analyzes a pandas DataFrame and determines appropriate MySQL data types along with maximum lengths for string columns:

```python
import pandas as pd
import numpy as np

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
            if df[column].apply(lambda x: isinstance(x, float) and not df[column].isnull().all():
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

## Usage Example

```python
# Example usage:
import pandas as pd

# Create a sample DataFrame
data = {
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'price': [10.99, 20.50, 15.75],
    'is_active': [True, False, True],
    'created_at': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
    'description': ['Short', 'Medium length description', 'Very long description that might exceed typical limits']
}

df = pd.DataFrame(data)

# Get schema info
schema = get_mysql_schema(df)
print("Schema Information:")
for col, info in schema.items():
    print(f"{col}: {info}")

# Generate CREATE TABLE statement
print("\nCREATE TABLE Statement:")
print(generate_mysql_create_table(df, 'users'))
```

## Key Features:

1. **Data Type Mapping**:
   - Maps pandas dtypes to appropriate MySQL data types
   - Handles integers, floats, strings, booleans, and datetimes

2. **String Length Calculation**:
   - Calculates maximum length for VARCHAR columns
   - Adds a buffer (20% or minimum 10 characters)
   - Automatically suggests TEXT for long strings

3. **Integer Optimization**:
   - Selects the smallest appropriate integer type (TINYINT, SMALLINT, etc.)
   - Determines whether UNSIGNED is appropriate

4. **Decimal Detection**:
   - Attempts to detect decimal numbers and suggests DECIMAL type with appropriate precision

5. **Nullability Detection**:
   - Checks for null values to determine NOT NULL constraints

6. **CREATE TABLE Generation**:
   - Includes a helper function to generate a complete CREATE TABLE statement

This function provides a comprehensive analysis of your DataFrame to help create an optimized MySQL schema.
