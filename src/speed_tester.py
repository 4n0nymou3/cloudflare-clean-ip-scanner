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
            response = requests.get(self.test_url, timeout=self.timeout, proxies={"http": ip, "https": ip})
            if response.status_code == 200:
                end_time = time.time()
                download_time = end_time - start_time
                speed_bps = len(response.content) * 8 / download_time
                speed_mbps = speed_bps / 1_000_000
                return speed_mbps
            else:
                return 0.0
        except:
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
