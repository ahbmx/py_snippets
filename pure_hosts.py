import requests
import json
from datetime import datetime
import argparse
from tabulate import tabulate

# Disable SSL warnings (only for testing with self-signed certs)
requests.packages.urllib3.disable_warnings()

class PureStorageMonitor:
    def __init__(self, array_ip, api_token):
        self.base_url = f"https://{array_ip}/api/2.x"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.verify_ssl = False  # Set to True for production with valid certs

    # Previous methods (get_array_capacity, get_data_reduction, etc.) remain the same...

    def get_hosts(self):
        """Get list of hosts with their WWNs"""
        url = f"{self.base_url}/hosts"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        hosts = response.json()
        
        # Get WWNs for each host
        for host in hosts:
            wwn_url = f"{self.base_url}/hosts/{host['name']}/host-wwns"
            wwn_response = requests.get(wwn_url, headers=self.headers, verify=self.verify_ssl)
            host['wwns'] = [wwn['wwn'] for wwn in wwn_response.json()]
            
            # Get host groups for each host
            hgroup_url = f"{self.base_url}/hosts/{host['name']}/host-groups"
            hgroup_response = requests.get(hgroup_url, headers=self.headers, verify=self.verify_ssl)
            host['host_groups'] = [hg['name'] for hg in hgroup_response.json()]
        
        return hosts

    def get_host_groups(self):
        """Get list of host groups with their members"""
        url = f"{self.base_url}/host-groups"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        host_groups = response.json()
        
        for group in host_groups:
            members_url = f"{self.base_url}/host-groups/{group['name']}/hosts"
            members_response = requests.get(members_url, headers=self.headers, verify=self.verify_ssl)
            group['hosts'] = [host['name'] for host in members_response.json()]
        
        return host_groups

    def generate_report(self, json_output=False):
        """Generate a comprehensive report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "capacity": self.get_array_capacity(),
            "data_reduction": self.get_data_reduction(),
            "health": self.get_array_health(),
            "alerts": self.get_alerts(),
            "volumes": self.get_volumes_space(),
            "hosts": self.get_hosts(),
            "host_groups": self.get_host_groups()
        }

        if json_output:
            return json.dumps(report, indent=2)
        else:
            return self._format_human_report(report)

    def _format_human_report(self, report):
        """Format the report for human-readable output"""
        output = []
        output.append(f"=== Pure Storage FlashArray Report ===")
        output.append(f"Generated at: {report['timestamp']}")
        
        # Previous sections (capacity, data reduction, health, etc.) remain the same...

        # Hosts Information
        hosts = report['hosts']
        output.append("\n--- Hosts Configuration ---")
        if not hosts:
            output.append("No hosts configured")
        else:
            host_table = []
            for host in hosts:
                host_table.append([
                    host['name'],
                    len(host['wwns']),
                    ", ".join(host['wwns'][:2]) + ("..." if len(host['wwns']) > 2 else ""),
                    ", ".join(host['host_groups']) or "None"
                ])
            output.append(tabulate(host_table, 
                                 headers=["Host Name", "WWN Count", "Sample WWNs", "Host Groups"],
                                 tablefmt="grid"))
        
        # Host Groups Information
        host_groups = report['host_groups']
        output.append("\n--- Host Groups ---")
        if not host_groups:
            output.append("No host groups configured")
        else:
            hg_table = []
            for group in host_groups:
                hg_table.append([
                    group['name'],
                    len(group['hosts']),
                    ", ".join(group['hosts'][:3]) + ("..." if len(group['hosts']) > 3 else "")
                ])
            output.append(tabulate(hg_table,
                                  headers=["Host Group", "Member Count", "Sample Members"],
                                  tablefmt="grid"))
        
        return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Pure Storage FlashArray Monitoring Script')
    parser.add_argument('--array-ip', required=True, help='FlashArray IP or hostname')
    parser.add_argument('--api-token', required=True, help='API token for authentication')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    args = parser.parse_args()

    monitor = PureStorageMonitor(args.array_ip, args.api_token)
    report = monitor.generate_report(json_output=args.json)
    print(report)

if __name__ == "__main__":
    main()
