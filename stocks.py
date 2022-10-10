# local imports
import requests
import time

# third party imports
from typing import Dict
from prettytable import PrettyTable
from bs4 import BeautifulSoup


def scrape_stock_info(stock_sym: str) -> Dict[str, str]:
    """Visits Yahoo Finance and scrapes the desired company's stock information.

    Args:
        sym: Company's stock symbol 
    Returns:
        Dict: All relevant information.
    """

    # Yahoo Finance site extraction
    BASEURL = f'https://finance.yahoo.com/quote/{stock_sym}?p={stock_sym}'

    try:
        source = requests.get(BASEURL)
    except AttributeError:
        print('Stock symbol does not exist.')

    # HTTP Response
    status = source.status_code
    print(f'HTTP Response [{status}]')

    soup = BeautifulSoup(source.text, 'lxml')

    company_name = soup.find('h1', class_='D(ib) Fz(18px)')
    stock_info = soup.find('div', class_='D(ib) Mend(20px)')
    stock_price = stock_info.find(
        class_='Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)')

    # Grab stock price (+ or -)
    stock_price_change = ''
    try:
        stock_price_change = stock_info.find(
            class_='Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)'
        ).get_text()
    except AttributeError:
        print('Stock dropped...')
        print('Gathering dropped price...')

        stock_price_change = stock_info.find(
            class_='Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)'
        ).get_text()

    market_close = stock_info.find('div', id='quote-market-notice')

    # Quote Summary
    summary_table = soup.find('div', id='quote-summary')
    row_title = summary_table.find_all(class_='C($primaryColor) W(51%)')
    row_data = summary_table.find_all(class_='Ta(end) Fw(600) Lh(14px)')

    table_data = zip(row_title, row_data)

    stock_summary = {}  # Stores scrapped info

    # Append scrapped data to dictionary
    stock_summary['Company'] = company_name.get_text()
    stock_summary['Stock Price'] = stock_price.get_text()
    stock_summary['Stock Price Change'] = stock_price_change
    stock_summary['Market close'] = market_close.get_text()

    for title, data in table_data:
        quote_title = title.get_text()
        quote_data = data.get_text()
        stock_summary[quote_title] = quote_data

    return stock_summary


def main():

    market_symbol = input(
        'Enter the company\'s stock symbol (e.g. AAPL for Apple): ').upper()

    scraping = True
    while scraping:
        print('Scraping...')

        company_summary = scrape_stock_info(market_symbol)

        # Get time
        named_tuple = time.localtime()
        time_string = time.strftime('%m/%d/%Y, %H:%M:%S', named_tuple)

        # Create table
        quote_table = PrettyTable()
        quote_table.field_names = ['Title', 'Data']  # Headers

        # Add all items to the table
        for title, data in company_summary.items():
            quote_table.add_row([title, data])

        quote_table_data = quote_table.get_string(
        )  # Convert table into string

        with open('Stock_Data.txt', 'a', encoding='utf-8') as f:
            f.write('\n\n')
            f.write(f'Scraped on: {time_string}\n')
            f.write(quote_table_data)

        print('Scrape complete.')

        time.sleep(5)


if __name__ == '__main__':
    main()
