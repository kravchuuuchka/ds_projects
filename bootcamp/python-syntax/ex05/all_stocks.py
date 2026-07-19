import sys


def all_stocks(query):
    COMPANIES = {
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Netflix': 'NFLX',
        'Tesla': 'TSLA',
        'Nokia': 'NOK'
    }

    STOCKS = {
        'AAPL': 287.73,
        'MSFT': 173.79,
        'NFLX': 416.90,
        'TSLA': 724.88,
        'NOK': 3.37
    }

    items = query.split(',')
    for item in items:
        if item.strip() == '':
            return
 
    for item in items:
        name = item.strip().title()
        ticker = item.strip().upper()
 
        if name in COMPANIES:
            print(f"{name} stock price is {STOCKS[COMPANIES[name]]}")
        elif ticker in STOCKS:
            company = [c for c, t in COMPANIES.items() if t == ticker][0]
            print(f"{ticker} is a ticker symbol for {company}")
        else:
            print(f"{item.strip()} is an unknown company or an unknown ticker symbol")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        all_stocks(sys.argv[1])