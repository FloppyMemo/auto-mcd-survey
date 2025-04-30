#!/usr/bin/env python3
"""
Automated McDonald's "Food for Thoughts" survey scraper.
Supports single or batch processing, configurable retries, delays,
parallel execution, logging to file, and interactive prompts with retry.
"""
import time
import random
import argparse
import re
import logging
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ensure webdriver-manager is available; install at runtime if missing
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"])
    from webdriver_manager.chrome import ChromeDriverManager


def split_receipt(code: str) -> tuple:
    """
    Normalize and split a 12-character receipt code into three 4-char segments.
    Raises ValueError for invalid codes.
    """
    raw = re.sub(r"[^A-Za-z0-9]", "", code)
    if len(raw) != 12:
        raise ValueError(f"Receipt code must be 12 alphanumeric chars, got '{code}'")
    return raw[:4], raw[4:8], raw[8:]


def setup_driver(headless: bool) -> webdriver.Chrome:
    """Initialize Chrome WebDriver with optional headless mode."""
    opts = Options()
    if headless:
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
    else:
        logging.info("Running with browser UI enabled.")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(60)
    return driver


def get_with_retry(driver, url: str, attempts: int, delay_min: float, delay_max: float) -> bool:
    """
    Try loading URL up to `attempts` times, waiting random between delay_min and delay_max seconds.
    Returns True on success, False on persistent failure.
    """
    for i in range(1, attempts + 1):
        try:
            driver.get(url)
            time.sleep(random.uniform(delay_min, delay_max))
            src = driver.page_source or ''
            if 'HTTP ERROR 504' not in src and len(src.strip()) > 1000:
                return True
            logging.warning("Attempt %d/%d: blank or error page, retrying...", i, attempts)
        except Exception as e:
            logging.warning("Attempt %d/%d: exception loading URL: %s", i, attempts, e)
    return False


def process_receipt(receipt_code: str, amount: str, opts: dict) -> str:
    """
    Run the survey flow for a single receipt; return the offer code or raise.
    """
    cn1, cn2, cn3 = split_receipt(receipt_code)
    amt_main, amt_dec = amount.split('.') if '.' in amount else (amount, '00')
    amt_main = amt_main.zfill(3)
    amt_dec = amt_dec.ljust(2, '0')[:2]

    driver = setup_driver(opts['headless'])
    try:
        logging.info("Processing receipt %s with amount %s", receipt_code, amount)
        # Step 1: Welcome page
        if not get_with_retry(driver, opts['start_url'], opts['attempts'], opts['delay_min'], opts['delay_max']):
            raise RuntimeError("Failed to load welcome page after retries")
        WebDriverWait(driver, opts['element_timeout']).until(
            EC.element_to_be_clickable((By.ID, "NextButton"))
        ).click()

        # Step 2: Enter coupon and amount
        WebDriverWait(driver, opts['element_timeout']).until(
            EC.presence_of_element_located((By.ID, "CN1"))
        )
        driver.find_element(By.ID, "CN1").send_keys(cn1)
        driver.find_element(By.ID, "CN2").send_keys(cn2)
        driver.find_element(By.ID, "CN3").send_keys(cn3)
        driver.find_element(By.ID, "AmountSpent1").send_keys(amt_main)
        driver.find_element(By.ID, "AmountSpent2").send_keys(amt_dec)
        driver.find_element(By.ID, "NextButton").click()

        # Step 3: Progress through survey pages
        while 'ValCode' not in driver.page_source:
            try:
                btn = WebDriverWait(driver, opts['element_timeout']).until(
                    EC.element_to_be_clickable((By.ID, "NextButton"))
                )
                labels = driver.find_elements(By.CSS_SELECTOR, "label.radioSimpleInput")
                if labels:
                    labels[0].click()
                btn.click()
                time.sleep(random.uniform(1, 2))
            except Exception:
                logging.debug("Reloading survey page due to error or timeout")
                if not get_with_retry(driver, driver.current_url, opts['attempts'], opts['delay_min'], opts['delay_max']):
                    raise RuntimeError("Max retries reached on survey page")

        # Step 4: Extract offer code
        code_elem = WebDriverWait(driver, opts['element_timeout']).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.ValCode"))
        )
        offer_code = code_elem.text.split(':', 1)[1].strip()
        logging.info("Got offer code %s for receipt %s", offer_code, receipt_code)
        return offer_code
    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Batch or single-run McDonald's survey scraper"
    )
    parser.add_argument('receipt_code', nargs='?', help="12-char receipt code")
    parser.add_argument('--amount', dest='amount', default='00.00',
                        help="Amount spent, e.g., '5.50'")
    parser.add_argument('--batch-file', type=Path, help="File with 'receipt,amount' lines")
    parser.add_argument('--output', type=Path, default=Path('results.csv'), help="CSV output file")
    parser.add_argument('--workers', type=int, default=1, help="Parallel threads for batch mode")
    parser.add_argument('--log-file', type=Path, default=Path('scraper.log'), help="Log file path")
    parser.add_argument('--headless', dest='headless', action='store_true', default=False,
                        help="Run browser in headless mode")
    parser.add_argument('--no-headless', dest='headless', action='store_false', help=argparse.SUPPRESS)
    parser.add_argument('--attempts', type=int, default=5, help="Page load retry attempts")
    parser.add_argument('--delay-min', type=float, default=3.0, help="Min delay between retries")
    parser.add_argument('--delay-max', type=float, default=8.0, help="Max delay between retries")
    parser.add_argument('--element-timeout', type=int, default=15, help="Timeout for element waits")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting scraper; headless=%s", args.headless)

    opts = vars(args)
    opts['start_url'] = "https://www.mcdfoodforthoughts.com/"

    # Interactive mode: prompt and retry until success
    if not args.batch_file and args.workers == 1 and not args.receipt_code:
        results = []
        while True:
            rc = input("Digite o código de 12 caracteres do recibo: ").strip()
            amt = input("Digite o valor da compra (ex: 5.50): ").strip()
            try:
                offer = process_receipt(rc, amt, opts)
                results.append((rc, amt, offer))
                break
            except Exception as e:
                logging.error("Falha para %s: %s. Tente novamente...", rc, e)
                time.sleep(random.uniform(opts['delay_min'], opts['delay_max']))

        # Write CSV
        with args.output.open('w', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(['receipt_code', 'amount', 'offer_code'])
            writer.writerows(results)
        logging.info("Processing complete. Results saved to %s", args.output)
        return

    # Prepare receipt list for batch or CLI args
    jobs = []
    if args.batch_file:
        with args.batch_file.open('r') as f:
            for line in f:
                part = line.strip().split(',')
                if part:
                    rc = part[0].strip()
                    amt = part[1].strip() if len(part) > 1 else args.amount
                    jobs.append((rc, amt))
    else:
        jobs.append((args.receipt_code, args.amount))

    results = []
    # Batch or CLI processing
    if args.workers > 1 and len(jobs) > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            future_map = {ex.submit(process_receipt, rc, amt, opts): (rc, amt) for rc, amt in jobs}
            for fut in as_completed(future_map):
                rc, amt = future_map[fut]
                try:
                    code = fut.result()
                except Exception as e:
                    logging.error("Error for %s: %s", rc, e)
                    code = ''
                results.append((rc, amt, code))
    else:
        for rc, amt in jobs:
            try:
                code = process_receipt(rc, amt, opts)
            except Exception as e:
                logging.error("Error for %s: %s", rc, e)
                code = ''
            results.append((rc, amt, code))

    # Write CSV for non-interactive
    with args.output.open('w', newline='') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(['receipt_code', 'amount', 'offer_code'])
        writer.writerows(results)

    logging.info("Processing complete. Results saved to %s", args.output)


if __name__ == '__main__':
    main()
