import json
import time
import requests
from typing import List, Dict

class SpeedTester:
    def __init__(self, config: Dict):
        self.test_url = config["speed_test_url"]
        self.min_speed_mbps = config["min_speed_mbps"]
        self.timeout = config["speed_test_timeout"]

    def test_download_speed(self, ip: str) -> float:
        try:
            start_time = time.time()
            response = requests.get(self.test_url, timeout=self.timeout)
            response.raise_for_status()
            end_time = time.time()
            download_time = end_time - start_time
            speed_bps = len(response.content) * 8 / download_time
            speed_mbps = speed_bps / 1_000_000
            print(f"IP: {ip}, Speed: {speed_mbps:.2f} Mbps")
            return speed_mbps
        except requests.exceptions.Timeout:
            print(f"IP: {ip}, Timeout occurred")
            return 0.0
        except requests.exceptions.RequestException as e:
            print(f"IP: {ip}, Error: {e}")
            return 0.0

    def filter_fast_ips(self, ips: Dict[str, List[str]]) -> Dict[str, List[str]]:
        fast_ips = {"ipv4": [], "ipv6": []}
        for ip_type, ip_list in ips.items():
            for ip in ip_list:
                speed = self.test_download_speed(ip)
                if speed >= self.min_speed_mbps:
                    fast_ips[ip_type].append(ip)
        return fast_ips

def run_speed_test():
    with open("config.json", "r") as f:
        config = json.load(f)
    with open(config["output_file"], "r") as f:
        ips = json.load(f)
    tester = SpeedTester(config)
    fast_ips = tester.filter_fast_ips(ips)
    with open(config["fast_ips_file"], "w") as f:
        json.dump(fast_ips, f, indent=4)

if __name__ == "__main__":
    run_speed_test()