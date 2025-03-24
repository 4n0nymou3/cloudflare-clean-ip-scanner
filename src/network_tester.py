import asyncio
import time
import socket
import subprocess
from typing import Dict, List, Tuple, Optional
import random
from concurrent.futures import ThreadPoolExecutor
from .utils import format_ip

class NetworkTester:
    def __init__(self, ports: List[int], timeout: int = 2, retry_count: int = 3):
        self.ports = ports
        self.timeout = timeout
        self.retry_count = retry_count

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

    async def _test_ip(self, ip: str) -> Tuple[str, float]:
        best_port = None
        best_latency = float('inf')
        for port in self.ports:
            success, latency = self._test_connection(ip, port)
            if success and latency < best_latency:
                best_latency = latency
                best_port = port
        return ip, best_port, best_latency

    async def test_ips(self, ips: Dict[str, List[str]]) -> Dict[str, List[str]]:
        working_ips = {"ipv4": [], "ipv6": []}
        tasks = []
        for ip_type, ip_list in ips.items():
            for ip in ip_list:
                tasks.append(self._test_ip(ip))
        results = await asyncio.gather(*tasks)
        for ip, port, latency in results:
            if port is not None:
                formatted_ip = format_ip(ip, port)
                if ':' in ip:
                    working_ips["ipv6"].append(formatted_ip)
                else:
                    working_ips["ipv4"].append(formatted_ip)
        return working_ips
