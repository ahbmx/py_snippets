import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings (only for testing with self-signed certificates)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class VMAXClient:
    def __init__(self, host, username, password, verify_ssl=False):
        self.base_url = f"https://{host}/univmax/restapi"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'version': '90'  # Adjust version based on your Unisphere version
        }
        
    def get_array_capacity(self, array_id):
        """Get capacity information for a specific array"""
        url = f"{self.base_url}/90/sloprovisioning/symmetrix/{array_id}"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_array_health_status(self, array_id):
        """Get health status for a specific array"""
        url = f"{self.base_url}/90/system/symmetrix/{array_id}/health"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_all_arrays(self):
        """Get list of all arrays managed by Unisphere"""
        url = f"{self.base_url}/90/system/symmetrix"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def print_capacity_info(capacity_data):
    """Print formatted capacity information"""
    print("\nArray Capacity Information:")
    print("=" * 50)
    
    # Extract relevant capacity metrics
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
    
    # Print component health if available
    components = health_info.get('component_health', [])
    if components:
        print("\nComponent Health:")
        for comp in components:
            print(f"  {comp.get('name', 'Unknown')}: {comp.get('status', 'Unknown')}")

def main():
    # Configuration - replace with your details
    unisphere_host = "your-unisphere-host"
    username = "your-username"
    password = "your-password"
    array_id = "your-array-id"  # e.g., "000123456789"
    verify_ssl = False  # Set to True for production with valid certificates
    
    # Create client
    client = VMAXClient(unisphere_host, username, password, verify_ssl)
    
    try:
        # Get and print array capacity
        capacity_data = client.get_array_capacity(array_id)
        print_capacity_info(capacity_data)
        
        # Get and print health status
        health_data = client.get_array_health_status(array_id)
        print_health_status(health_data)
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")

if __name__ == "__main__":
    main()
