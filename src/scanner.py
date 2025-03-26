import asyncio
import json
import os
import time
from typing import Dict, List
from .domain_resolver import DomainResolver
from .ip_validator import IPValidator
from .network_tester import NetworkTester
from .cidr_ranges import CIDRRangeScanner
from .utils import load_config, save_json

class CloudflareIPScanner:
    def __init__(self, config_path: str = "config.json"):
        self.config = load_config(config_path)
        self.domain_resolver = DomainResolver(self.config["target_domains"])
        self.ip_validator = IPValidator(
            ipv4_ranges=self.config["cloudflare_ipv4_ranges"],
            ipv6_ranges=self.config["cloudflare_ipv6_ranges"]
        )
        self.network_tester = NetworkTester(
            ports=self.config["test_ports"],
            timeout=self.config["connection_timeout"],
            retry_count=self.config["retry_count"],
            download_test_url=self.config["download_test_url"],
            min_download_speed=self.config["min_download_speed"],
            region_filter=self.config["region_filter"]
        )
        self.cidr_scanner = CIDRRangeScanner(
            ipv4_ranges=self.config["cloudflare_ipv4_ranges"],
            ipv6_ranges=self.config["cloudflare_ipv6_ranges"]
        )
        self.min_ipv4 = self.config["min_ips"]["ipv4"]
        self.min_ipv6 = self.config["min_ips"]["ipv6"]
        self.max_ipv4 = self.config["max_ips"]["ipv4"]
        self.max_ipv6 = self.config["max_ips"]["ipv6"]
        self.default_ipv4 = self.config["default_ipv4"]
        self.default_ipv6 = self.config["default_ipv6"]
        self.output_file = self.config["output_file"]
        self.scan_results_file = self.config["scan_results_file"]
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    async def scan(self) -> Dict[str, List[str]]:
        start_time = time.time()
        resolved_ips = await self.domain_resolver.resolve_all()
        ipv4_set = {ip for ip in resolved_ips["ipv4"] if self.ip_validator.is_cloudflare_ipv4(ip)}
        ipv6_set = {ip for ip in resolved_ips["ipv6"] if self.ip_validator.is_cloudflare_ipv6(ip)}
        if len(ipv4_set) < self.min_ipv4 or len(ipv6_set) < self.min_ipv6:
            cidr_ips = await self.cidr_scanner.scan_random_ips(
                ipv4_count=max(0, self.min_ipv4 - len(ipv4_set)),
                ipv6_count=max(0, self.min_ipv6 - len(ipv6_set))
            )
            ipv4_set.update(cidr_ips["ipv4"])
            ipv6_set.update(cidr_ips["ipv6"])
        working_ips = await self.network_tester.test_ips({
            "ipv4": list(ipv4_set),
            "ipv6": list(ipv6_set)
        })
        if len(working_ips["ipv4"]) < self.min_ipv4:
            working_ips["ipv4"].extend(self.default_ipv4[:self.min_ipv4 - len(working_ips["ipv4"])])
        if len(working_ips["ipv6"]) < self.min_ipv6:
            working_ips["ipv6"].extend(self.default_ipv6[:self.min_ipv6 - len(working_ips["ipv6"])])
        working_ips["ipv4"] = working_ips["ipv4"][:self.max_ipv4]
        working_ips["ipv6"] = working_ips["ipv6"][:self.max_ipv6]
        scan_time = time.time() - start_time
        scan_stats = {
            "timestamp": time.time(),
            "duration_seconds": scan_time,
            "domains_scanned": len(self.config["target_domains"]),
            "ips_discovered": {
                "ipv4": len(ipv4_set),
                "ipv6": len(ipv6_set)
            },
            "working_ips_found": {
                "ipv4": len(working_ips["ipv4"]),
                "ipv6": len(working_ips["ipv6"])
            }
        }
        save_json(self.scan_results_file, scan_stats)
        save_json(self.output_file, working_ips)
        return working_ips

    def run(self):
        return asyncio.run(self.scan())