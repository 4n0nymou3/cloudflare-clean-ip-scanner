import asyncio
import socket
import random
from typing import Dict, List, Set
import dns.resolver

class DomainResolver:
    def __init__(self, domains: List[str]):
        self.domains = domains
        self.resolvers = [
            "1.1.1.1",
            "1.0.0.1",
            "8.8.8.8",
            "8.8.4.4",
            "9.9.9.9",
            "149.112.112.112"
        ]

    async def _resolve_domain(self, domain: str) -> Dict[str, Set[str]]:
        ipv4_set = set()
        ipv6_set = set()
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [random.choice(self.resolvers)]
        resolver.timeout = 2
        resolver.lifetime = 5
        try:
            answers = resolver.resolve(domain, 'A')
            for rdata in answers:
                ipv4_set.add(str(rdata))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            pass
        try:
            answers = resolver.resolve(domain, 'AAAA')
            for rdata in answers:
                ipv6_set.add(f"[{str(rdata)}]")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            pass
        if not ipv4_set and not ipv6_set:
            try:
                addrinfo = socket.getaddrinfo(domain, None)
                for family, _, _, _, sockaddr in addrinfo:
                    if family == socket.AF_INET:
                        ipv4_set.add(sockaddr[0])
                    elif family == socket.AF_INET6:
                        ipv6_set.add(f"[{sockaddr[0]}]")
            except socket.gaierror:
                pass
        return {
            "domain": domain,
            "ipv4": ipv4_set,
            "ipv6": ipv6_set
        }

    async def resolve_all(self) -> Dict[str, List[str]]:
        tasks = [self._resolve_domain(domain) for domain in self.domains]
        results = await asyncio.gather(*tasks)
        all_ipv4 = set()
        all_ipv6 = set()
        for result in results:
            all_ipv4.update(result["ipv4"])
            all_ipv6.update(result["ipv6"])
        return {
            "ipv4": list(all_ipv4),
            "ipv6": list(all_ipv6)
        }
