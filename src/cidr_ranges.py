import random
import ipaddress
from typing import Dict, List, Set
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CIDRRangeScanner:
    def __init__(self, ipv4_ranges: List[str], ipv6_ranges: List[str]):
        self.ipv4_networks = [ipaddress.IPv4Network(cidr) for cidr in ipv4_ranges]
        self.ipv6_networks = [ipaddress.IPv6Network(cidr) for cidr in ipv6_ranges]
        self.high_priority_ipv4 = [
            ipaddress.IPv4Network("188.114.96.0/20"),
            ipaddress.IPv4Network("162.158.0.0/15"),
            ipaddress.IPv4Network("162.159.0.0/16")
        ]
        self.high_priority_ipv6 = [
            ipaddress.IPv6Network("2606:4700::/32"),
            ipaddress.IPv6Network("2400:cb00::/32")
        ]

    def _generate_random_ipv4(self, count: int) -> Set[str]:
        ips = set()
        high_priority_count = int(count * 0.9)
        for _ in range(high_priority_count):
            network = random.choice(self.high_priority_ipv4)
            host = random.randint(0, network.num_addresses - 1)
            ip = str(network[host])
            ips.add(ip)
        remaining_count = count - len(ips)
        for _ in range(remaining_count):
            network = random.choice(self.ipv4_networks)
            host = random.randint(0, min(network.num_addresses - 1, 1000000))
            ip = str(network[host])
            ips.add(ip)
        return ips

    def _generate_random_ipv6(self, count: int) -> Set[str]:
        ips = set()
        high_priority_count = int(count * 0.9)
        for _ in range(high_priority_count):
            network = random.choice(self.high_priority_ipv6)
            host_part = [random.randint(0, 65535) for _ in range(4)]
            ip_int = int(network.network_address) + (host_part[0] << 48) + (host_part[1] << 32) + (host_part[2] << 16) + host_part[3]
            ip = str(ipaddress.IPv6Address(ip_int))
            ips.add(f"[{ip}]")
        remaining_count = count - len(ips)
        for _ in range(remaining_count):
            network = random.choice(self.ipv6_networks)
            host_part = [random.randint(0, 65535) for _ in range(4)]
            ip_int = int(network.network_address) + (host_part[0] << 48) + (host_part[1] << 32) + (host_part[2] << 16) + host_part[3]
            ip = str(ipaddress.IPv6Address(ip_int))
            ips.add(f"[{ip}]")
        return ips

    async def scan_random_ips(self, ipv4_count: int = 30, ipv6_count: int = 15) -> Dict[str, List[str]]:
        with ThreadPoolExecutor() as executor:
            ipv4_task = asyncio.get_event_loop().run_in_executor(
                executor, self._generate_random_ipv4, ipv4_count * 2
            )
            ipv6_task = asyncio.get_event_loop().run_in_executor(
                executor, self._generate_random_ipv6, ipv6_count * 2
            )
            ipv4_ips, ipv6_ips = await asyncio.gather(ipv4_task, ipv6_task)
        return {
            "ipv4": list(ipv4_ips)[:ipv4_count],
            "ipv6": list(ipv6_ips)[:ipv6_count]
        }