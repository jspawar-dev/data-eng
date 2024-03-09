import requests
from bs4 import BeautifulSoup
import pandas as pd


def request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


def parse(soup):
    books = soup.findAll('div', class_='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16')
    print(len(books))
    data = []
    for book in books:
        item = {}
        try:
            item['Title'] = book.find('span', class_='a-size-medium a-color-base a-text-normal').get_text().strip()
            item['Price'] = book.find('span', class_='a-offscreen').get_text().strip()
            item['Author'] = book.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style').get_text().strip()
            item['Rating'] = book.find('span', class_='a-icon-alt').get_text().strip()
            item['Link'] = 'https://www.amazon.co.uk' + book.find('a',class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')['href']
        except AttributeError:
            item['Rating'] = 'No Rating'
        print(item)
        data.append(item)

    return data


def pagination(soup):
    try:
        next_page = soup.find('span', class_='s-pagination-strip')
        url = 'https://www.amazon.co.uk/' + str(next_page.find('a', class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator')['href'])
        return url
    except (AttributeError, TypeError):
        return


def saveToCSV(data, mode):
    df = pd.DataFrame(data)
    df.to_csv('books.csv', mode=mode, index=False, header=False)


def main():
    url = 'https://www.amazon.co.uk/s?k=data+engineering+books&crid=38DYM17O25O1K&sprefix=data+engineering+books%2Caps%2C118&ref=nb_sb_noss_1'

    saveToCSV([], 'w')
    while True:
        soup = request(url)
        data = parse(soup)
        saveToCSV(data, 'a')
        url = pagination(soup)
        if not url:
            break
        print(url)


main()
