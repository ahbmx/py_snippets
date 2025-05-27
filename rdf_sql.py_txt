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
