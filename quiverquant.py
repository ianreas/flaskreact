import os
import requests
import psycopg2
from datetime import datetime 
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class CongressionalTrade:
    """
    Simple data structure to hold trade information.
    """
    ticker: str
    stock_name: str
    politician_name: str
    politician_party: str
    transaction_type: str
    amount: str
    disclosed_date: str
    traded_date: str

@dataclass
class LobbyingDisclosure:
    """
    Holds lobbying disclosure data from each row of the table.
    """
    ticker: str
    amount: str
    issue: str
    date: str

def fetch_data():
    # Replicate the cURL command's headers in Python
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "_ga=GA1.1.645159745.1738024013; _tt_enable_cookie=1; _ttp=InMdxk29IN2ZHHfso2WhZAcrQws.tt.1; sm_anonymous_id=612f27b5-0e94-4169-9225-8800d3cd091c; _clck=1nj6ts%7C2%7Cfte%7C0%7C1854; csrftoken=DAU0O2mZtxFnCz2YeHvYAtxvlaHVlIIt0N88upAtg0jE2kjsM90D0HnCQJ9iad1O; sessionid=w2vxce5iir78143ob2ubiaw8dneuwsr2; cf_clearance=fYdnxz4SrQumNASNH.7oPoZQB91qOhxo.3tLl.rgv8M-1739479429-1.2.1.1-iFnLeGdzs9f1fcrnNTF8Fam0lFXVxl_0JXpq6OI_qm11G5X5L64hsv_vem5L5s0UHfXktLj5AFRl8.lXGIzXKkrbZNllWwhRJNcBQYXkaaskUrdtbwnu.tWXgCA0.Q71v97BpXMjXgQg.CpYWC0LvtXqpbhQq_fRu5sw8uIUsQp4fjpAvE18gAQNwWWzGJTlyRdYp8j2rHbsuyHH6yFQMqe9b594PuyaIKNMMENFt22_2DHJu63hgGO04zAQcwc5s.92M90i5dpcMmhswZFMlcsJYtbTa6VZzKSBWJ5qQuI; _clsk=qq5tcb%7C1739480117619%7C5%7C1%7Cx.clarity.ms%2Fcollect; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Feb+13+2025+15%3A55%3A17+GMT-0500+(Eastern+Standard+Time)&version=6.39.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false; AWSALB=XIAvl5dv1adFbCVbbPXI95Llk2FJFhxAp2D56JOExZc3m80cZpA6xWydXTyKetTHbScwTTkntfVr9Jf20M7cZDR4dr3Hi5vRbtNpvt2P1JR1ZTTXDEpzXPL3nExC; AWSALBCORS=XIAvl5dv1adFbCVbbPXI95Llk2FJFhxAp2D56JOExZc3m80cZpA6xWydXTyKetTHbScwTTkntfVr9Jf20M7cZDR4dr3Hi5vRbtNpvt2P1JR1ZTTXDEpzXPL3nExC; _ga_16X10F2F5T=GS1.1.1739479429.10.1.1739480312.60.0.0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    # The URL from the cURL
    url = "https://www.quiverquant.com/home/"
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    print(response.text)
    
    return response.text

def parse_congressional_trades_table(html_content: str) -> list[CongressionalTrade]:
    """
    Given the full HTML content (response.text), find the table with the given class
    and extract each row into a CongressionalTrade object.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    trades: list[CongressionalTrade] = []
    
    # Find the table by its class
    table = soup.find("table", class_="table-congressional-trades dataset-table")
    if not table:
        print("No table found with class 'table-congressional-trades dataset-table'")
        return trades
    
    # Find all rows inside the table body
    tbody = table.find("tbody")
    if not tbody:
        print("No <tbody> found inside the table.")
        return trades
    
    rows = tbody.find_all("tr")
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            # Skip row if it doesn't have the expected 4 cells
            continue
        
        # 1) Stock info (ticker and stock name)
        ticker_element = cells[0].find("strong")
        ticker = ticker_element.get_text(strip=True) if ticker_element else ""
        
        stock_name_element = cells[0].find("span", class_="hide-mobile")
        stock_name = stock_name_element.get_text(strip=True) if stock_name_element else ""
        
        # 2) Politician info (name and party)
        politician_name_element = cells[1].find("p")
        politician_name = politician_name_element.get_text(strip=True) if politician_name_element else ""
        
        politician_party_element = cells[1].find("span")
        politician_party = politician_party_element.get_text(strip=True) if politician_party_element else ""
        
        # 3) Transaction type and amount
        transaction_type_element = cells[2].find("strong")
        transaction_type = transaction_type_element.get_text(strip=True) if transaction_type_element else ""
        
        amount_element = cells[2].find("span")
        amount = amount_element.get_text(strip=True) if amount_element else ""
        
        # 4) Disclosure date and traded date
        disclosed_date_element = cells[3].find("p")
        disclosed_date = disclosed_date_element.get_text(strip=True) if disclosed_date_element else ""
        
        traded_date_element = cells[3].find("span")
        traded_date_text = traded_date_element.get_text(strip=True) if traded_date_element else ""
        # "Traded: Jan. 17" => extract just the date
        traded_date = traded_date_text.replace("Traded: ", "")
        
        # Construct the CongressionalTrade object
        trade_record = CongressionalTrade(
            ticker=ticker,
            stock_name=stock_name,
            politician_name=politician_name,
            politician_party=politician_party,
            transaction_type=transaction_type,
            amount=amount,
            disclosed_date=disclosed_date,
            traded_date=traded_date
        )
        
        trades.append(trade_record)
    
    return trades

def parse_corporate_lobbying_table(html_content: str) -> list[LobbyingDisclosure]:
    """
    Given the full HTML content, look for the <table> with class="dataset-table"
    inside the 'dataset-lobbying carousel-slide' element, then extract row data
    into LobbyingDisclosure objects.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    results: list[LobbyingDisclosure] = []
    
    # Find the <li> container or directly the <table> with class="dataset-table"
    lobbying_li = soup.find("li", class_="dataset dataset-lobbying carousel-slide")
    if not lobbying_li:
        print("No <li> element found with the classes 'dataset-lobbying carousel-slide'.")
        return results
    
    table = lobbying_li.find("table", class_="dataset-table")
    if not table:
        print("No table found with class 'dataset-table' inside the lobbying container.")
        return results
    
    tbody = table.find("tbody")
    if not tbody:
        print("No <tbody> found in the lobbying table.")
        return results
    
    # Each <tr> in <tbody> corresponds to one record
    rows = tbody.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            # Skip if unexpected structure
            continue
        
        # 1) Ticker
        #    A typical cell structure: 
        #    <td><a href="../stock/RY/">RY</a><span class="hide-desktop">Feb. 13, ..</span></td>
        ticker_link = cells[0].find("a")
        ticker = ticker_link.get_text(strip=True) if ticker_link else ""
        
        # 2) Amount
        amount = cells[1].get_text(strip=True)
        
        # 3) Issue
        issue = cells[2].get_text(strip=True)
        
        # 4) Date
        #    Usually in the 4th cell with class="date hide-mobile"
        #    e.g. "Feb. 13, 2025, 12:19 p.m."
        date_text = cells[3].get_text(strip=True)
        
        # Create a LobbyingDisclosure instance
        disclosure = LobbyingDisclosure(
            ticker=ticker,
            amount=amount,
            issue=issue,
            date=date_text
        )
        
        results.append(disclosure)
    
    return results

def upload_congress_trading_data_to_db(trades: list[CongressionalTrade]):
    """
    Insert congressional trading data (list of CongressionalTrade objects)
    into the 'congressional_trading' table in Postgres.
    """

    # Use your actual Postgres connection URL
    database_url = "postgresql://postgres:muhammedik10@paas-backend-1.cbigmg0cgxs7.us-east-1.rds.amazonaws.com:5432/paas_backend"

    # Connect to the database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    try:
        for trade in trades:
            cursor.execute(
                """
                INSERT INTO congressional_trading (
                    ticker,
                    politican_name,
                    politician_party,
                    transaction_type,
                    disclosed_date
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    trade.ticker,
                    trade.politician_name,
                    trade.politician_party,
                    trade.transaction_type,
                    trade.disclosed_date,
                ),
            )

        conn.commit()

    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def upload_lobbying_data_to_db(disclosures: list[LobbyingDisclosure]):
    """
    Insert lobbying data (list of LobbyingDisclosure objects)
    into the 'lobbying' table in Postgres.
    """

    # Use your actual Postgres connection URL
    database_url = "postgresql://postgres:muhammedik10@paas-backend-1.cbigmg0cgxs7.us-east-1.rds.amazonaws.com:5432/paas_backend"

    # Connect to the database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    try:
        for disclosure in disclosures:
            cursor.execute(
                """
                INSERT INTO corporate_lobbying (
                    ticker,
                    amount,
                    issue,
                    date
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    disclosure.ticker,
                    disclosure.amount,
                    disclosure.issue,
                    disclosure.date,
                ),
            )

        conn.commit()

    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        data = fetch_data()
        # congress_trading_data = parse_congressional_trades_table(data)
        # print(congress_trading_data)
        # upload_congress_trading_data_to_db(congress_trading_data)
        # print("Congressional trading data successfully fetched and stored.")

        lobbying_data = parse_corporate_lobbying_table(data)
        print(lobbying_data)
        upload_lobbying_data_to_db(lobbying_data)
        print("Lobbying data successfully fetched and stored.")
    except Exception as e:
        # In a real-world scenario, you might log this or notify yourself
        print(f"An error occurred: {e}")




