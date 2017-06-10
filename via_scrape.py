import requests
import bs4
from twilio.rest import Client

from config import credentials, tel_numbers


URL = 'http://www.viarail.ca/en/deals/halifax-montreal'


def scrape_via_site():
    """Request html for train website and scrape the table of offers."""
    res = requests.get(URL)
    res.raise_for_status()
    via_soup = bs4.BeautifulSoup(res.text)

    data = []
    table = via_soup.find('table')
    rows = table.findAll('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols:
            data.append([ele for ele in cols if ele])

    msg = create_msg_for_text(data)
    return msg


def create_msg_for_text(data):
    """Parse rows in tables to look for dates."""
    res = set()
    for row in data:
        for item in row:
            if 'aug' in item.lower():
                # TODO replace string slice with regex
                date = 'Aug: ' + item[:10]
                res.add(date)

    return res


def send_txt_msg(msg):
    """Send text message via Twilio with msg as the body."""
    account_sid, auth_token = credentials()
    to_number, from_number = tel_numbers()
    client = Client(account_sid, auth_token)

    client.messages.create(
        to=to_number,
        from_=from_number,
        body='Dates found:' + str(msg))


def main():
    print('Commencing scrape of website')
    msg = scrape_via_site()
    print('Scraping complete')
    send_txt_msg(msg)
    print('Text message sent')


if __name__ == '__main__':
    main()