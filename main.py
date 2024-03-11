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

            title = book.find('span', class_='a-size-medium a-color-base a-text-normal')
            if title:
                item['Title'] = title.text.strip()
            else:
                continue

            price = book.find('span', class_='a-offscreen')
            if price and price.text.strip() != '£0.00':
                item['Price'] = price.text.strip()
            else:
                continue

            author = book.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')
            if author:
                item['Author'] = author.text.strip()
            else:
                item['Author'] = 'No Author'
                # continue

            rating = book.find('span', class_='a-icon-alt')
            if rating:
                item['Rating'] = rating.text.strip()
            else:
                item['Rating'] = 'No Rating'

            link = book.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')['href']
            if link:
                item['Link'] = 'https://www.amazon.co.uk' + link
            else:
                item['Link'] = 'No Link'
        except AttributeError:
            continue

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
