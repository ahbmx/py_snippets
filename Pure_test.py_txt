import requests
import json
from datetime import datetime
import argparse

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

    def get_array_capacity(self):
        """Get array capacity and space usage metrics"""
        url = f"{self.base_url}/arrays/space"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        return response.json()

    def get_data_reduction(self):
        """Get data reduction metrics"""
        url = f"{self.base_url}/arrays/data-reduction"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        return response.json()

    def get_alerts(self):
        """Get active alerts"""
        url = f"{self.base_url}/alerts?filter=state='open'"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        return response.json()

    def get_array_health(self):
        """Get array health status"""
        url = f"{self.base_url}/arrays/status"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        return response.json()

    def get_volumes_space(self):
        """Get volumes space usage"""
        url = f"{self.base_url}/volumes?space=true"
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        return response.json()

    def bytes_to_human(self, bytes_size):
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    def generate_report(self, json_output=False):
        """Generate a comprehensive report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "capacity": self.get_array_capacity(),
            "data_reduction": self.get_data_reduction(),
            "health": self.get_array_health(),
            "alerts": self.get_alerts(),
            "volumes": self.get_volumes_space()
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
        
        # Capacity Summary
        capacity = report['capacity']
        output.append("\n--- Capacity Summary ---")
        output.append(f"Total Physical Capacity: {self.bytes_to_human(capacity['capacity'])}")
        output.append(f"Used Physical Space: {self.bytes_to_human(capacity['space']['total_physical'])}")
        output.append(f"Unique Data: {self.bytes_to_human(capacity['space']['unique'])}")
        output.append(f"Snapshot Space: {self.bytes_to_human(capacity['space']['snapshots'])}")
        output.append(f"Data Reduction Ratio: {capacity['data_reduction']:.2f}:1")
        
        # Data Reduction
        dr = report['data_reduction']
        output.append("\n--- Data Reduction Details ---")
        output.append(f"Total Reduction: {dr['total_reduction']:.2f}:1")
        output.append(f"Deduplication: {dr['deduplication']:.2f}:1")
        output.append(f"Compression: {dr['compression']:.2f}:1")
        
        # Health Status
        health = report['health']
        output.append("\n--- Array Health ---")
        output.append(f"Status: {'HEALTHY' if health['status'] == 'ok' else 'DEGRADED'}")
        output.append(f"Version: {health['version']}")
        
        # Alerts
        alerts = report['alerts']
        output.append("\n--- Active Alerts ---")
        if not alerts:
            output.append("No active alerts")
        else:
            for alert in alerts:
                output.append(f"[{alert['severity']}] {alert['component_name']}: {alert['summary']}")
        
        # Volumes Summary
        volumes = report['volumes']
        output.append("\n--- Volumes Summary ---")
        output.append(f"Total Volumes: {len(volumes)}")
        if volumes:
            vol = volumes[0]  # Just show first volume as example
            output.append(f"Sample Volume '{vol['name']}':")
            output.append(f"  Provisioned: {self.bytes_to_human(vol['size'])}")
            output.append(f"  Used: {self.bytes_to_human(vol['space'])}")
            output.append(f"  Data Reduction: {vol['data_reduction']:.2f}:1")
        
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
