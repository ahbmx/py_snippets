import requests
import json
import time
import csv
from concurrent.futures import ThreadPoolExecutor

# Configuration
UNISPHERE_IP = "your_unisphere_ip"
USERNAME = "your_username"
PASSWORD = "your_password"
SYMMETRIX_ID = "000123456789"
BATCH_SIZE = 20
OUTPUT_DIR = "/tmp/rdf_reports"
MAX_WORKERS = 5  # Concurrent API calls

# Setup session
session = requests.Session()
session.auth = (USERNAME, PASSWORD)
session.headers.update({'content-type': 'application/json'})
session.verify = False  # Set to True with valid cert

def get_rdf_status(sg_name):
    """Get RDF status for a single storage group"""
    url = f"https://{UNISPHERE_IP}/univmax/restapi/90/replication/symmetrix/{SYMMETRIX_ID}/storagegroup/{sg_name}/rdf"
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            return {sg_name: response.json()}
        return {sg_name: f"Error: {response.status_code}"}
    except Exception as e:
        return {sg_name: f"Exception: {str(e)}"}

def process_batch(batch, batch_num):
    """Process a batch of storage groups"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_DIR}/rdf_batch_{batch_num}_{timestamp}.json"
    csv_file = f"{OUTPUT_DIR}/rdf_summary_{batch_num}_{timestamp}.csv"
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(get_rdf_status, batch))
    
    # Save detailed JSON output
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create CSV summary
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Storage Group', 'RDFG Number', 'State', 'Mode', 'Status'])
        
        for result in results:
            for sg, data in result.items():
                if isinstance(data, dict):
                    for rdf_group in data.get('rdfGroupInfo', []):
                        writer.writerow([
                            sg,
                            rdf_group.get('rdfgNumber'),
                            rdf_group.get('state'),
                            rdf_group.get('mode'),
                            rdf_group.get('status')
                        ])
    
    return len(results)

def main():
    # Get all storage groups with RDF
    url = f"https://{UNISPHERE_IP}/univmax/restapi/90/replication/symmetrix/{SYMMETRIX_ID}/storagegroup?rdf=true"
    response = session.get(url)
    storage_groups = response.json()['name']
    
    # Split into batches
    batches = [storage_groups[i:i + BATCH_SIZE] for i in range(0, len(storage_groups), BATCH_SIZE)]
    
    # Process batches with delay between them
    for i, batch in enumerate(batches, 1):
        print(f"Processing batch {i} of {len(batches)} with {len(batch)} groups")
        processed = process_batch(batch, i)
        print(f"Completed batch {i}, processed {processed} groups")
        
        # Delay between batches (seconds)
        if i < len(batches):
            time.sleep(10)

if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()
