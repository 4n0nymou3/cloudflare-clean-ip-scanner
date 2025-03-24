import asyncio
from src.scanner import CloudflareIPScanner

if __name__ == "__main__":
    scanner = CloudflareIPScanner()
    asyncio.run(scanner.scan())
