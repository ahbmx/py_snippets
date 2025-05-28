# Python Function to Display Data in Tabular Format Using Pandas

Here's an enhanced version that incorporates pandas for more powerful table display options:

```python
import pandas as pd

def display_table(data, headers=None, style='grid', max_col_width=30, max_rows=None, 
                  show_index=False, float_format="%.2f", **kwargs):
    """
    Display data in a tabular format using pandas.
    
    Parameters:
    - data: List of lists/dicts or pandas DataFrame containing the table data
    - headers: List of column headers (optional if data is DataFrame or dict)
    - style: Table style ('grid', 'pretty', 'simple', 'html', 'latex', etc.)
    - max_col_width: Maximum column width before truncation
    - max_rows: Maximum number of rows to display (None for all)
    - show_index: Whether to show the index column
    - float_format: Format string for floating point numbers
    - **kwargs: Additional arguments passed to pandas DataFrame.to_string()
    """
    
    # Convert input data to pandas DataFrame
    if isinstance(data, pd.DataFrame):
        df = data
    elif isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data, columns=headers)
    
    # Apply display options
    pd.set_option('display.max_colwidth', max_col_width)
    if max_rows is not None:
        pd.set_option('display.max_rows', max_rows)
    
    # Display the table based on selected style
    if style.lower() == 'grid':
        from tabulate import tabulate
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=show_index, 
                      floatfmt=float_format, **kwargs))
    elif style.lower() == 'pretty':
        print(df.to_string(index=show_index, float_format=float_format, **kwargs))
        print("\n" + "-" * 80)  # Footer line
    elif style.lower() == 'html':
        from IPython.display import display, HTML
        display(HTML(df.to_html(index=show_index, float_format=float_format, **kwargs)))
    else:
        # Use pandas default formatting for other styles
        print(df.to_string(index=show_index, float_format=float_format, **kwargs))
```

## Example Usage:

```python
# Example 1: From list of lists with headers
data = [
    ["John Doe", 28, "Software Engineer", "john@example.com"],
    ["Jane Smith", 32, "Data Scientist", "jane.smith@example.org"],
    ["Bob Johnson", 45, "Project Manager", None],
    ["Alice Brown", 23, "Intern", "alice.brown@company.com"]
]
headers = ["Name", "Age", "Position", "Email"]

display_table(data, headers, style='grid')

# Example 2: From dictionary
employee_data = {
    'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
    'Age': [28, 32, 45, 23],
    'Salary': [85000.5678, 92000.1234, 110000.9876, 45000.0]
}

display_table(employee_data, style='pretty', float_format="%.1f")

# Example 3: Using pandas DataFrame directly
import pandas as pd
df = pd.DataFrame({
    'Product': ['Laptop', 'Phone', 'Tablet', 'Monitor'],
    'Price': [999.99, 699.50, 329.99, 199.99],
    'Stock': [45, 120, 80, 35]
})

display_table(df, style='html')  # Will display in Jupyter notebook
```

## Key Features:

1. **Multiple Input Formats**: Accepts lists, dictionaries, or pandas DataFrames
2. **Flexible Display Styles**:
   - `grid`: Nicely formatted ASCII grid (requires `tabulate`)
   - `pretty`: Simple formatted table with footer
   - `html`: HTML output for Jupyter notebooks
   - Default pandas formatting for other styles

3. **Number Formatting**: Control over floating point display
4. **Size Control**: Column width and row limits
5. **Index Control**: Option to show/hide index column

## Dependencies:

- pandas (required)
- tabulate (required for 'grid' style - install with `pip install tabulate`)
- IPython (required for HTML display in Jupyter notebooks)

This implementation gives you the power of pandas' data handling with flexible display options suitable for both console and notebook environments.
