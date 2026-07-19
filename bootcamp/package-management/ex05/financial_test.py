#!/usr/bin/env python3
import sys
import time

import pytest
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

    time.sleep(5)

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


# --- Fixtures ---

@pytest.fixture(scope="module")
def msft_revenue() -> tuple[str, ...]:
    return get_financial_data("MSFT", "Total Revenue")


@pytest.fixture(scope="module")
def aapl_net_income() -> tuple[str, ...]:
    return get_financial_data("AAPL", "Net Income")


# --- Tests ---

class TestFetchPageRequests: 
    def test_returns_beautifulsoup(self) -> None:
        result = fetch_page_requests("MSFT")
        assert isinstance(result, BeautifulSoup)
 
    def test_html_contains_ticker(self) -> None:
        result = fetch_page_requests("MSFT")
        assert "MSFT" in result.text
 
    def test_invalid_ticker_returns_empty_result(self) -> None:
        soup = fetch_page_requests("INVALIDTICKER123")
        result = extract_field(soup, "Total Revenue")
        assert result == ()
 
 
class TestFetchPagePlaywright: 
    def test_returns_beautifulsoup(self) -> None:
        result = fetch_page_playwright("AAPL", "Net Income")
        assert isinstance(result, BeautifulSoup)
 
    def test_html_contains_ticker(self) -> None:
        result = fetch_page_playwright("AAPL", "Net Income")
        assert "AAPL" in result.text
 
    def test_invalid_ticker_returns_empty_result(self) -> None:
        soup = fetch_page_playwright("INVALIDTICKER123", "Net Income")
        result = extract_field(soup, "Net Income")
        assert result == ()
 
 
class TestExtractField: 
    def test_returns_empty_tuple_when_field_missing(self) -> None:
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        result = extract_field(soup, "Total Revenue")
        assert result == ()
 
    def test_first_element_is_field_name(self, msft_revenue: tuple[str, ...]) -> None:
        assert msft_revenue[0] == "Total Revenue"
 
    def test_returns_tuple(self, msft_revenue: tuple[str, ...]) -> None:
        assert isinstance(msft_revenue, tuple)
 
 
class TestGetFinancialData: 
    def test_returns_tuple(self, msft_revenue: tuple[str, ...]) -> None:
        assert isinstance(msft_revenue, tuple)
 
    def test_all_elements_are_strings(self, msft_revenue: tuple[str, ...]) -> None:
        assert all(isinstance(v, str) for v in msft_revenue)
 
    def test_has_multiple_values(self, msft_revenue: tuple[str, ...]) -> None:
        assert len(msft_revenue) > 1
 
    def test_total_revenue_first_element(self, msft_revenue: tuple[str, ...]) -> None:
        assert msft_revenue[0] == "Total Revenue"
 
    def test_total_revenue_returns_revenue_data(self, msft_revenue: tuple[str, ...]) -> None:
        assert any(any(c.isdigit() for c in v) for v in msft_revenue[1:])
 
    def test_invalid_ticker_raises(self) -> None:
        with pytest.raises(Exception):
            get_financial_data("INVALIDTICKER123", "Total Revenue")
 
    def test_invalid_field_raises(self) -> None:
        with pytest.raises(Exception):
            get_financial_data("MSFT", "Nonexistent Field XYZ")
 
 
class TestGetFinancialDataPlaywright: 
    def test_returns_tuple(self, aapl_net_income: tuple[str, ...]) -> None:
        assert isinstance(aapl_net_income, tuple)
 
    def test_all_elements_are_strings(self, aapl_net_income: tuple[str, ...]) -> None:
        assert all(isinstance(v, str) for v in aapl_net_income)
 
    def test_first_element_is_field_name(self, aapl_net_income: tuple[str, ...]) -> None:
        assert aapl_net_income[0] == "Net Income"
 
    def test_has_multiple_values(self, aapl_net_income: tuple[str, ...]) -> None:
        assert len(aapl_net_income) > 1
 
    def test_net_income_contains_numeric_values(self, aapl_net_income: tuple[str, ...]) -> None:
        assert any(any(c.isdigit() for c in v) for v in aapl_net_income[1:])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./financial_test.py 'MSFT' 'Total Revenue'")
        sys.exit(1)

    try:
        result = get_financial_data(sys.argv[1], sys.argv[2])
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)