# Cloudflare Clean IP Scanner

Advanced scanner for discovering and testing clean Cloudflare IPs with automated periodic scanning, performance metrics, and comprehensive IP coverage for both IPv4 and IPv6.

## Features

- Discovers clean Cloudflare IPs from multiple sources
- Tests connectivity and response time for discovered IPs
- Supports both IPv4 and IPv6 addresses
- Automatically runs every 15 minutes via GitHub Actions
- Updates the IPs JSON file with the best performing IPs
- Comprehensive scanning of Cloudflare IP ranges
- Advanced filtering and validation mechanisms

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure settings in `config.json` if needed
4. Run manually: `python scripts/run_scan.py`

## Automated Scanning

This repository is configured to run the IP scanner automatically every 15 minutes using GitHub Actions. The results are updated in the `data/ips.json` file.

## Configuration

Edit the `config.json` file to customize:

- Target domains for scanning
- Cloudflare CIDR ranges to check
- Ports to test
- Test timeouts and retry settings
- Minimum number of IPs to collect

## License

MIT License - See LICENSE file for details