import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from src.scanner import CloudflareIPScanner

if __name__ == "__main__":
    scanner = CloudflareIPScanner()
    asyncio.run(scanner.scan())