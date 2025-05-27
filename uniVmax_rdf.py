import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlencode

# Disable SSL warnings (only for testing with self-signed certificates)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class VMAXClient:
    def __init__(self, host, username, password, verify_ssl=False, api_version='90'):
        self.base_url = f"https://{host}/univmax/restapi"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.api_version = api_version
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'version': self.api_version
        }
        
    def _get_paginated(self, url, params=None, limit=1000):
        """Helper method to handle paginated requests"""
        if params is None:
            params = {}
        params['pageSize'] = limit
        results = []
        
        while True:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check if the response contains paginated results
            if isinstance(data, dict) and 'resultList' in data:
                results.extend(data['resultList']['result'])
                if 'nextPageKey' in data['resultList'] and data['resultList']['nextPageKey']:
                    params['pageKey'] = data['resultList']['nextPageKey']
                else:
                    break
            else:
                # Non-paginated response
                return data
        
        return results
    
    def get_array_capacity(self, array_id):
        """Get capacity information for a specific array"""
        url = f"{self.base_url}/{self.api_version}/sloprovisioning/symmetrix/{array_id}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_array_health_status(self, array_id):
        """Get health status for a specific array"""
        url = f"{self.base_url}/{self.api_version}/system/symmetrix/{array_id}/health"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_all_arrays(self):
        """Get list of all arrays managed by Unisphere"""
        url = f"{self.base_url}/{self.api_version}/system/symmetrix"
        return self._get_paginated(url)
    
    def get_replication_groups(self, array_id):
        """Get all replication groups for an array"""
        url = f"{self.base_url}/{self.api_version}/replication/symmetrix/{array_id}/rdf_group"
        return self._get_paginated(url)
    
    def get_replication_group_details(self, array_id, rdf_group_number):
        """Get detailed status for a specific replication group"""
        url = f"{self.base_url}/{self.api_version}/replication/symmetrix/{array_id}/rdf_group/{rdf_group_number}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_storage_groups_with_replication(self, array_id):
        """Get storage groups with replication configurations"""
        url = f"{self.base_url}/{self.api_version}/replication/symmetrix/{array_id}/storagegroup"
        return self._get_paginated(url)

def print_capacity_info(capacity_data):
    """Print formatted capacity information"""
    print("\nArray Capacity Information:")
    print("=" * 50)
    
    symmetrix_info = capacity_data.get('symmetrix', [{}])[0]
    total_cap = symmetrix_info.get('total_cap_gb', 0)
    used_cap = symmetrix_info.get('used_cap_gb', 0)
    free_cap = symmetrix_info.get('free_cap_gb', 0)
    sub_cap = symmetrix_info.get('subscribed_cap_gb', 0)
    
    print(f"Total Capacity (GB): {total_cap:,.2f}")
    print(f"Used Capacity (GB): {used_cap:,.2f} ({used_cap/total_cap*100:.1f}%)")
    print(f"Free Capacity (GB): {free_cap:,.2f} ({free_cap/total_cap*100:.1f}%)")
    print(f"Subscribed Capacity (GB): {sub_cap:,.2f} ({sub_cap/total_cap*100:.1f}%)")
    print(f"Subscription Ratio: {sub_cap/used_cap:.2f}:1" if used_cap > 0 else "N/A")

def print_health_status(health_data):
    """Print formatted health status"""
    print("\nArray Health Status:")
    print("=" * 50)
    
    health_info = health_data.get('health', {})
    status = health_info.get('health_score', {}).get('symmetrix_health', "Unknown")
    num_alerts = health_info.get('num_failed_components', 0)
    
    print(f"Overall Health Status: {status}")
    print(f"Number of Active Alerts: {num_alerts}")
    
    components = health_info.get('component_health', [])
    if components:
        print("\nComponent Health:")
        for comp in components:
            print(f"  {comp.get('name', 'Unknown')}: {comp.get('status', 'Unknown')}")

def print_replication_groups(replication_groups, client, array_id):
    """Print replication group information"""
    print("\nReplication Groups Status:")
    print("=" * 50)
    
    if not replication_groups:
        print("No replication groups found")
        return
    
    for group in replication_groups:
        rdfg_number = group.get('rdfgNumber')
        if rdfg_number:
            details = client.get_replication_group_details(array_id, rdfg_number)
            print(f"\nRDF Group {rdfg_number}:")
            print(f"  Label: {group.get('label', 'N/A')}")
            print(f"  Type: {group.get('type', 'N/A')}")
            print(f"  State: {details.get('states', {}).get('state', 'N/A')}")
            print(f"  Mode: {details.get('modes', {}).get('mode', 'N/A')}")
            print(f"  Remote Symmetrix: {details.get('remoteSymmetrix', 'N/A')}")
            print(f"  Number of Pairs: {details.get('numDevices', 0)}")

def print_storage_groups_with_replication(storage_groups):
    """Print storage groups with replication"""
    print("\nStorage Groups with Replication:")
    print("=" * 50)
    
    if not storage_groups:
        print("No storage groups with replication found")
        return
    
    for sg in storage_groups:
        print(f"\nStorage Group: {sg.get('storageGroupId')}")
        print(f"  SRP: {sg.get('srp', 'N/A')}")
        print(f"  Service Level: {sg.get('service_level', 'N/A')}")
        print(f"  RDF Groups: {', '.join(str(g) for g in sg.get('rdfgs', []))}")
        print(f"  Replication Mode: {sg.get('replication_mode', 'N/A')}")

def main():
    # Configuration - replace with your details
    unisphere_host = "your-unisphere-host"
    username = "your-username"
    password = "your-password"
    array_id = "your-array-id"  # e.g., "000123456789"
    verify_ssl = False  # Set to True for production with valid certificates
    api_version = '90'  # Adjust based on your Unisphere version
    
    # Create client
    client = VMAXClient(unisphere_host, username, password, verify_ssl, api_version)
    
    try:
        # Get and print array capacity
        capacity_data = client.get_array_capacity(array_id)
        print_capacity_info(capacity_data)
        
        # Get and print health status
        health_data = client.get_array_health_status(array_id)
        print_health_status(health_data)
        
        # Get and print replication groups
        replication_groups = client.get_replication_groups(array_id)
        print_replication_groups(replication_groups, client, array_id)
        
        # Get and print storage groups with replication
        storage_groups = client.get_storage_groups_with_replication(array_id)
        print_storage_groups_with_replication(storage_groups)
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        if err.response.status_code == 401:
            print("Authentication failed - check username and password")
        elif err.response.status_code == 404:
            print("Resource not found - check array ID")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")

if __name__ == "__main__":
    main()
