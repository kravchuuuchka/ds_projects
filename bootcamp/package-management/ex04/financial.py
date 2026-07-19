#!/usr/bin/env python3
import sys
import time

import requests
from bs4 import BeautifulSoup


def fetch_page_requests(ticker: str) -> BeautifulSoup:
    url = f"https://finance.yahoo.com/quote/{ticker.upper()}/financials"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    #time.sleep(5)

    response = requests.Session().get(url, headers=headers, timeout=15)

    if response.status_code != 200:
        raise Exception(f"URL not found or invalid ticker (status: {response.status_code})")

    if "consent" in response.url or "Guiding our users" in response.text:
        raise Exception("Yahoo blocked the request with a consent page. Try again later.")

    return BeautifulSoup(response.text, "html.parser")


def fetch_page_playwright(ticker: str, field_name: str) -> BeautifulSoup:
    from playwright.sync_api import sync_playwright

    url = f"https://finance.yahoo.com/quote/{ticker.upper()}/financials"

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="commit", timeout=60000)
        time.sleep(5)

        if "consent" in page.url or "Guiding our users" in page.content():
            browser.close()
            raise Exception("Yahoo blocked the request with a consent page. Try again later.")

        clicked: set[str | None] = set()
        while True:
            soup = BeautifulSoup(page.content(), "html.parser")
            if extract_field(soup, field_name):
                break

            buttons = page.query_selector_all("button.icon-btn[data-ylk*='elm:expand']")
            new_buttons = [b for b in buttons if b.get_attribute("aria-label") not in clicked]

            if not new_buttons:
                break

            for button in new_buttons:
                label = button.get_attribute("aria-label")
                try:
                    button.click()
                    time.sleep(1)
                except Exception:
                    pass
                finally:
                    clicked.add(label)

        html = page.content()
        browser.close()

    return BeautifulSoup(html, "html.parser")


def extract_field(soup: BeautifulSoup, field_name: str) -> tuple[str, ...]:
    normalized = field_name.strip().lower()

    row_title = soup.find(
        "div",
        attrs={"title": lambda t: t and t.strip().lower() == normalized},
    )

    if not row_title:
        return ()

    row = row_title.find_parent("div", class_=lambda c: c and "row" in c)
    if not row:
        return ()

    value_divs = row.find_all("div", class_=lambda c: c and "column" in c)
    values = [div.get_text(strip=True) for div in value_divs[1:] if div.get_text(strip=True)]

    if not values:
        return ()

    return (field_name, *values)


def get_financial_data(ticker: str, field_name: str) -> tuple[str, ...]:
    soup = fetch_page_requests(ticker)
    result = extract_field(soup, field_name)

    if result:
        return result

    soup = fetch_page_playwright(ticker, field_name)
    result = extract_field(soup, field_name)

    if result:
        return result

    raise Exception(f"Field '{field_name}' not found on the page.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./financial.py 'MSFT' 'Total Revenue'")
        sys.exit(1)

    try:
        result = get_financial_data(sys.argv[1], sys.argv[2])
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)