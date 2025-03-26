import ipaddress
from typing import List

class IPValidator:
    def __init__(self, ipv4_ranges: List[str], ipv6_ranges: List[str]):
        self.ipv4_networks = [ipaddress.IPv4Network(cidr) for cidr in ipv4_ranges]
        self.ipv6_networks = [ipaddress.IPv6Network(cidr) for cidr in ipv6_ranges]

    def is_cloudflare_ipv4(self, ip: str) -> bool:
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            return any(ip_obj in network for network in self.ipv4_networks)
        except ValueError:
            return False

    def is_cloudflare_ipv6(self, ip: str) -> bool:
        try:
            if ip.startswith('[') and ip.endswith(']'):
                ip = ip[1:-1]
            ip_obj = ipaddress.IPv6Address(ip)
            return any(ip_obj in network for network in self.ipv6_networks)
        except ValueError:
            return False

    def is_cloudflare_ip(self, ip: str) -> bool:
        if ':' in ip:
            return self.is_cloudflare_ipv6(ip)
        else:
            return self.is_cloudflare_ipv4(ip)

    def filter_cloudflare_ips(self, ips: List[str]) -> List[str]:
        return [ip for ip in ips if self.is_cloudflare_ip(ip)]
