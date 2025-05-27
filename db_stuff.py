import pandas as pd
import sqlite3
from sqlite3 import OperationalError
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StorageArrayDatabase:
    def __init__(self, db_name='storage_metrics.db'):
        """Initialize the database connection and setup."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        
        # Define the expected tables and their optimized structures
        self.tables_schema = {
            'array_metrics': {
                'columns': {
                    'timestamp': 'DATETIME',
                    'array_id': 'VARCHAR(50)',
                    'array_name': 'VARCHAR(100)',
                    'total_capacity_gb': 'DECIMAL(12,2)',
                    'used_capacity_gb': 'DECIMAL(12,2)',
                    'free_capacity_gb': 'DECIMAL(12,2)',
                    'iops': 'INTEGER',
                    'throughput_mbps': 'DECIMAL(10,2)',
                    'latency_ms': 'DECIMAL(10,2)',
                    'status': 'VARCHAR(20)'
                },
                'indexes': ['timestamp', 'array_id']
            },
            'disk_metrics': {
                'columns': {
                    'timestamp': 'DATETIME',
                    'disk_id': 'VARCHAR(50)',
                    'array_id': 'VARCHAR(50)',
                    'capacity_gb': 'DECIMAL(10,2)',
                    'used_gb': 'DECIMAL(10,2)',
                    'status': 'VARCHAR(20)',
                    'read_errors': 'INTEGER',
                    'write_errors': 'INTEGER'
                },
                'indexes': ['timestamp', 'disk_id', 'array_id']
            },
            'volume_metrics': {
                'columns': {
                    'timestamp': 'DATETIME',
                    'volume_id': 'VARCHAR(50)',
                    'array_id': 'VARCHAR(50)',
                    'size_gb': 'DECIMAL(12,2)',
                    'used_gb': 'DECIMAL(12,2)',
                    'iops': 'INTEGER',
                    'throughput_mbps': 'DECIMAL(10,2)',
                    'latency_ms': 'DECIMAL(10,2)'
                },
                'indexes': ['timestamp', 'volume_id', 'array_id']
            }
        }
        
        self.initialize_database()
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute('PRAGMA journal_mode = WAL')  # Better concurrency
            self.conn.execute('PRAGMA synchronous = NORMAL')  # Good balance between safety and speed
            self.conn.execute('PRAGMA cache_size = -10000')  # 10MB cache
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database {self.db_name}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def initialize_database(self):
        """Create tables if they don't exist with optimized schema."""
        try:
            for table_name, table_def in self.tables_schema.items():
                # Create table
                columns_sql = []
                for col_name, col_type in table_def['columns'].items():
                    columns_sql.append(f"{col_name} {col_type}")
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns_sql)}
                )
                """
                self.cursor.execute(create_table_sql)
                
                # Create indexes
                for index_col in table_def.get('indexes', []):
                    index_name = f"idx_{table_name}_{index_col}"
                    self.cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON {table_name}({index_col})
                    """)
            
            self.conn.commit()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            self.conn.rollback()
            raise
    
    def detect_column_types(self, df):
        """
        Detect appropriate SQL column types and max lengths from a pandas DataFrame.
        Returns a dictionary of column_name: (sql_type, max_length) pairs.
        """
        type_mapping = {
            'int64': 'INTEGER',
            'float64': 'DECIMAL(10,2)',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'DATETIME',
            'object': 'VARCHAR'  # Default for strings
        }
        
        column_info = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Handle datetime separately
            if np.issubdtype(df[col].dtype, np.datetime64):
                column_info[col] = ('DATETIME', None)
                continue
            
            # Handle numeric types
            if np.issubdtype(df[col].dtype, np.integer):
                column_info[col] = ('INTEGER', None)
            elif np.issubdtype(df[col].dtype, np.floating):
                column_info[col] = ('DECIMAL(12,2)', None)
            # Handle strings and objects
            elif dtype == 'object':
                # Calculate max length for string columns
                max_len = df[col].astype(str).str.len().max()
                if pd.isna(max_len):
                    max_len = 50  # default length if all values are NA
                column_info[col] = (f'VARCHAR({int(max_len)})', int(max_len))
            else:
                # Fallback to TEXT if type not recognized
                column_info[col] = ('TEXT', None)
        
        return column_info
    
    def create_table_from_dataframe(self, table_name, df, primary_key=None):
        """
        Create a new table optimized for the given DataFrame.
        Automatically detects column types and max lengths.
        """
        try:
            # Detect column types
            column_info = self.detect_column_types(df)
            
            # Generate column definitions
            columns_sql = []
            for col, (col_type, _) in column_info.items():
                col_def = f"{col} {col_type}"
                if primary_key and col == primary_key:
                    col_def += " PRIMARY KEY"
                columns_sql.append(col_def)
            
            # Create table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns_sql)}
            )
            """
            
            self.cursor.execute(create_table_sql)
            
            # Add indexes for timestamp and ID columns if they exist
            if 'timestamp' in df.columns:
                self.cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp 
                ON {table_name}(timestamp)
                """)
            
            id_columns = [col for col in df.columns if col.endswith('_id')]
            for id_col in id_columns:
                self.cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_{id_col} 
                ON {table_name}({id_col})
                """)
            
            self.conn.commit()
            logger.info(f"Table {table_name} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            self.conn.rollback()
            return False
    
    def insert_dataframe(self, table_name, df, if_exists='append'):
        """
        Insert DataFrame data into the specified table.
        if_exists: 'append' (default), 'replace', or 'fail'
        """
        try:
            # Check if table exists
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not self.cursor.fetchone():
                # Table doesn't exist, create it
                self.create_table_from_dataframe(table_name, df)
            
            # Handle if_exists parameter
            if if_exists == 'replace':
                self.cursor.execute(f"DELETE FROM {table_name}")
            
            # Convert datetime columns to strings for SQLite
            for col in df.columns:
                if np.issubdtype(df[col].dtype, np.datetime64):
                    df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert data in batches for better performance
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                batch.to_sql(table_name, self.conn, if_exists='append', index=False)
            
            self.conn.commit()
            logger.info(f"Inserted {len(df)} rows into {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            self.conn.rollback()
            return False
    
    def optimize_database(self):
        """Perform database optimization tasks."""
        try:
            # Rebuild indexes
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"REINDEX {table_name}")
            
            # Vacuum to defragment and optimize storage
            self.cursor.execute("VACUUM")
            
            # Update statistics for query optimizer
            self.cursor.execute("ANALYZE")
            
            self.conn.commit()
            logger.info("Database optimization completed")
            return True
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close the database connection."""
        try:
            if self.conn:
                self.optimize_database()  # Optimize before closing
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Sample data for demonstration
    sample_metrics = {
        'timestamp': pd.date_range(start='2023-01-01', periods=5, freq='H'),
        'array_id': ['array1', 'array2', 'array3', 'array1', 'array2'],
        'array_name': ['Primary Storage', 'Backup Storage', 'Test Array', 'Primary Storage', 'Backup Storage'],
        'total_capacity_gb': [10240.5, 5120.25, 2048.0, 10240.5, 5120.25],
        'used_capacity_gb': [5120.25, 2560.125, 1024.0, 5220.3, 2600.5],
        'iops': [15000, 8000, 3000, 14500, 8200],
        'throughput_mbps': [1200.5, 600.25, 300.0, 1180.75, 610.5],
        'latency_ms': [2.5, 3.2, 5.1, 2.6, 3.3],
        'status': ['normal', 'normal', 'degraded', 'normal', 'normal']
    }
    
    df = pd.DataFrame(sample_metrics)
    
    # Create and populate the database
    db = StorageArrayDatabase('storage_metrics.db')
    
    # Example of creating a new table from a DataFrame
    db.create_table_from_dataframe('custom_metrics', df)
    
    # Example of inserting data
    db.insert_dataframe('array_metrics', df)
    
    # Example of optimizing the database
    db.optimize_database()
    
    # Close the connection
    db.close()
