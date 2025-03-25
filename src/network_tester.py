import asyncio
import time
import socket
import subprocess
from typing import Dict, List, Tuple, Optional
import random
from concurrent.futures import ThreadPoolExecutor
from .utils import format_ip
import requests

class NetworkTester:
    def __init__(self, ports: List[int], timeout: int = 2, retry_count: int = 3, download_test_url: str = "", min_download_speed: float = 1.0):
        self.ports = ports
        self.timeout = timeout
        self.retry_count = retry_count
        self.download_test_url = download_test_url
        self.min_download_speed = min_download_speed

    def _test_connection(self, ip: str, port: int) -> Tuple[bool, float]:
        start_time = time.time()
        is_ipv6 = ':' in ip
        test_ip = ip[1:-1] if ip.startswith('[') and ip.endswith(']') else ip
        for attempt in range(self.retry_count):
            try:
                sock = socket.socket(
                    socket.AF_INET6 if is_ipv6 else socket.AF_INET,
                    socket.SOCK_STREAM
                )
                sock.settimeout(self.timeout)
                result = sock.connect_ex((test_ip, port))
                sock.close()
                if result == 0:
                    latency = time.time() - start_time
                    return True, latency
            except (socket.timeout, socket.error):
                pass
            time.sleep(0.1)
        return False, 0.0

    def _test_download_speed(self, ip: str) -> float:
        try:
            start_time = time.time()
            response = requests.get(self.download_test_url, timeout=10)
            if response.status_code == 200:
                download_time = time.time() - start_time
                speed = len(response.content) / download_time / 1024 / 1024
                return speed
            else:
                return 0.0
        except Exception:
            return 0.0

    async def _test_ip(self, ip: str) -> Tuple[str, float, float]:
        best_port = None
        best_latency = float('inf')
        for port in self.ports:
            success, latency = self._test_connection(ip, port)
            if success and latency < best_latency:
                best_latency = latency
                best_port = port
        if best_port is not None:
            speed = self._test_download_speed(ip)
            if speed >= self.min_download_speed:
                return ip, best_port, best_latency, speed
        return ip, None, 0.0, 0.0

    async def test_ips(self, ips: Dict[str, List[str]]) -> Dict[str, List[str]]:
        working_ips = {"ipv4": [], "ipv6": []}
        tasks = []
        for ip_type, ip_list in ips.items():
            for ip in ip_list:
                tasks.append(self._test_ip(ip))
        results = await asyncio.gather(*tasks)
        for ip, port, latency, speed in results:
            if port is not None:
                formatted_ip = format_ip(ip, port)
                if ':' in ip:
                    working_ips["ipv6"].append(formatted_ip)
                else:
                    working_ips["ipv4"].append(formatted_ip)
        return working_ips