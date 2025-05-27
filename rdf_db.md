# PowerMax RDF Monitoring with MySQL Integration and Grafana Support

Here's a comprehensive solution to check RDF status across your PowerMax 8000 device groups, store the data in MySQL, and make it Grafana-ready with proper datetime fields.

## Solution Architecture

1. **Data Collection**: Python script using PowerMax REST API
2. **Database Schema**: Optimized MySQL table structure
3. **Grafana Integration**: Time-series friendly format

## MySQL Table Setup

```sql
CREATE DATABASE IF NOT EXISTS powermax_monitoring;

USE powermax_monitoring;

CREATE TABLE IF NOT EXISTS rdf_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collection_time DATETIME NOT NULL,
    symmetrix_id VARCHAR(16) NOT NULL,
    storage_group VARCHAR(128) NOT NULL,
    rdf_group_number INT,
    rdf_state VARCHAR(32),
    rdf_mode VARCHAR(32),
    rdf_status VARCHAR(32),
    volume_config VARCHAR(32),
    ra_group VARCHAR(32),
    ra_capacity VARCHAR(32),
    consistency_state VARCHAR(32),
    last_sync_time DATETIME,
    is_protected BOOLEAN,
    is_consistent BOOLEAN,
    INDEX (collection_time),
    INDEX (storage_group),
    INDEX (rdf_group_number),
    INDEX (rdf_state)
) ENGINE=InnoDB;
```

## Python Collector Script

```python
import requests
import mysql.connector
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import pytz

# Configuration
UNISPHERE_IP = "your_unisphere_ip"
USERNAME = "your_username"
PASSWORD = "your_password"
SYMMETRIX_ID = "000123456789"
BATCH_SIZE = 20
MAX_WORKERS = 5
COLLECTION_INTERVAL = 3600  # Seconds between full collections

# MySQL Configuration
DB_CONFIG = {
    'host': 'your_mysql_host',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'powermax_monitoring'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_rdf_status_record(cursor, collection_time, sg_name, rdf_data):
    """Insert RDF status record into MySQL"""
    query = """
    INSERT INTO rdf_status (
        collection_time, symmetrix_id, storage_group, rdf_group_number,
        rdf_state, rdf_mode, rdf_status, volume_config, ra_group,
        ra_capacity, consistency_state, last_sync_time, is_protected,
        is_consistent
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Parse last sync time if available
    last_sync = rdf_data.get('lastSyncTime')
    last_sync_time = datetime.strptime(last_sync, '%Y-%m-%d %H:%M:%S') if last_sync else None
    
    cursor.execute(query, (
        collection_time,
        SYMMETRIX_ID,
        sg_name,
        rdf_data.get('rdfgNumber'),
        rdf_data.get('state'),
        rdf_data.get('mode'),
        rdf_data.get('status'),
        rdf_data.get('volumeConfig'),
        rdf_data.get('raGroup'),
        rdf_data.get('raCapacity'),
        rdf_data.get('consistencyState'),
        last_sync_time,
        rdf_data.get('protected', False),
        rdf_data.get('consistent', False)
    ))

def get_rdf_status(session, sg_name):
    """Get RDF status for a single storage group"""
    url = f"https://{UNISPHERE_IP}/univmax/restapi/90/replication/symmetrix/{SYMMETRIX_ID}/storagegroup/{sg_name}/rdf"
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def process_storage_groups(storage_groups):
    """Process all storage groups and store in MySQL"""
    collection_time = datetime.now(pytz.utc)
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({'content-type': 'application/json'})
    session.verify = False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    processed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create futures for all storage groups
        futures = {executor.submit(get_rdf_status, session, sg): sg for sg in storage_groups}
        
        for future in futures:
            sg_name = futures[future]
            try:
                result = future.result()
                if 'rdfGroupInfo' in result:
                    for rdf_group in result['rdfGroupInfo']:
                        create_rdf_status_record(cursor, collection_time, sg_name, rdf_group)
                    processed += 1
                else:
                    print(f"Error processing {sg_name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Exception processing {sg_name}: {str(e)}")
    
    conn.commit()
    cursor.close()
    conn.close()
    return processed

def main():
    # Get all storage groups with RDF
    url = f"https://{UNISPHERE_IP}/univmax/restapi/90/replication/symmetrix/{SYMMETRIX_ID}/storagegroup?rdf=true"
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    response = session.get(url)
    
    if response.status_code != 200:
        print(f"Failed to get storage groups: HTTP {response.status_code}")
        return
    
    storage_groups = response.json().get('name', [])
    print(f"Found {len(storage_groups)} RDF storage groups")
    
    while True:
        start_time = time.time()
        print(f"Starting collection at {datetime.now(pytz.utc)}")
        
        processed = process_storage_groups(storage_groups)
        print(f"Completed collection. Processed {processed} storage groups")
        
        # Calculate sleep time accounting for processing duration
        processing_time = time.time() - start_time
        sleep_time = max(0, COLLECTION_INTERVAL - processing_time)
        print(f"Next collection in {sleep_time/60:.1f} minutes")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
```

## Grafana Integration

1. **MySQL Data Source Setup**:
   - Add MySQL as a data source in Grafana
   - Configure with your database credentials

2. **Sample Dashboard Queries**:

**RDF State Overview (Pie Chart)**:
```sql
SELECT 
    rdf_state AS "State",
    COUNT(*) AS "Count"
FROM rdf_status
WHERE collection_time >= $__timeFrom() AND collection_time <= $__timeTo()
GROUP BY rdf_state
```

**RDF Status Timeline (Time Series)**:
```sql
SELECT 
    collection_time AS "time",
    storage_group AS "Storage Group",
    CASE 
        WHEN rdf_state = 'Active' THEN 1
        WHEN rdf_state = 'Suspended' THEN 2
        WHEN rdf_state = 'Failed' THEN 3
        ELSE 0
    END AS "state_value"
FROM rdf_status
WHERE collection_time >= $__timeFrom() AND collection_time <= $__timeTo()
ORDER BY collection_time
```

**RDF Group Status Table**:
```sql
SELECT
    storage_group AS "Storage Group",
    rdf_group_number AS "RDF Group",
    rdf_state AS "State",
    rdf_mode AS "Mode",
    volume_config AS "Config",
    last_sync_time AS "Last Sync",
    consistency_state AS "Consistency"
FROM rdf_status
WHERE collection_time = (
    SELECT MAX(collection_time) 
    FROM rdf_status
)
ORDER BY rdf_state, storage_group
```

## Optimization Tips

1. **Database Indexing**:
   ```sql
   ALTER TABLE rdf_status ADD INDEX idx_composite (collection_time, rdf_state);
   ALTER TABLE rdf_status ADD INDEX idx_storage_group (storage_group(64));
   ```

2. **Partitioning for Large Datasets**:
   ```sql
   ALTER TABLE rdf_status PARTITION BY RANGE (TO_DAYS(collection_time)) (
       PARTITION p_2023 VALUES LESS THAN (TO_DAYS('2024-01-01')),
       PARTITION p_2024 VALUES LESS THAN (TO_DAYS('2025-01-01')),
       PARTITION p_future VALUES LESS THAN MAXVALUE
   );
   ```

3. **Data Retention Policy**:
   ```sql
   CREATE EVENT purge_old_rdf_status
   ON SCHEDULE EVERY 1 DAY
   DO
       DELETE FROM rdf_status WHERE collection_time < DATE_SUB(NOW(), INTERVAL 90 DAY);
   ```

Would you like me to add any specific features like:
- Alerting integration when RDF groups fail?
- Detailed synchronization metrics tracking?
- Delta reporting (only changes between collections)?
