import schedule
import time
from src.scanner import CloudflareIPScanner

def job():
    scanner = CloudflareIPScanner()
    scanner.run()

schedule.every(15).minutes.do(job)

if __name__ == "__main__":
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)
