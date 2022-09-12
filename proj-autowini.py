import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Safari()
SLACK_WEBHOOK_URL = "***"


def get_url(make, model, min_year, max_price):
    make = make.strip().replace(' ', '+')
    model = model.strip().replace(' ', '+')
    search_term = make + '-' + model
    url = f'https://www.autowini.com/Cars/{search_term}/car-search?i_sIndexVal=bq&i_sSearchType=quick&i_sStartYear={min_year}&i_sPriceTo={max_price}'
    return url


def get_html_autowini(url):
    driver.get(url)
    return driver.page_source


def extract_links():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all('li', {'class': 'list'})
    links = []
    for item in results:
        atag = item.find_all('a')[1].get('href')
        url = 'https://www.autowini.com' + str(atag)
        links.append(url)
    return links


def extract_pages(url):
    html = driver.page_source
    links = []
    for i in range(1, 3):
        curr_url = url + f'&i_iNowPageNo={i}'
        driver.get(curr_url)
        time.sleep(2)
        links += extract_links()
    return links


def construct_links_message_autowini(make, model, links):
    if len(links) == 0:
        return f"Found 0 existing {make} {model} deals \n\n\n"

    final_string = (
        f"Found {len(links)} {make} {model} deal(s) for the team to consider:\n\n"
    )
    for i in range(len(links)):
        final_string += f"{i+1}. {links[i]}\n"
    return final_string


def send_message_autowini(website, message):
    data = {"message": message, "website": website}
    requests.post(SLACK_WEBHOOK_URL, json=data)


def find_available_car_deals_from_autowini():
    make = 'Hyundai'
    model = 'Accent'
    min_year = '2015'
    max_price = '600'
    website = "https://autowini.com"
    url = get_url(make, model, min_year, max_price)
    get_html_autowini(url)
    links = extract_pages(url)
    results = construct_links_message_autowini(make, model, links)
    msg = "Search Results for Autowini:\n\n\n" + results
    send_message_autowini(website, msg)
    driver.close()


find_available_car_deals_from_autowini()
