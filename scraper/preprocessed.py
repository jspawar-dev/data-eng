import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2


def request(url): # This function sends a request to the url that is provided and returns a soup object with the web pages html.
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


def parse(soup): # This function finds every book on the web page and parses through and extracts the information. It returns the books in a list.
    books = soup.findAll('div', class_='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16')
    print(len(books))
    data = []
    for book in books:
        item = {}
        try:

            title = book.find('span', class_='a-size-medium a-color-base a-text-normal')
            if title:
                item['Title'] = title.text.strip().replace('′', '')
            else:
                continue

            price = book.find('span', class_='a-offscreen')
            if price and price.text.strip() != '£0.00':
                item['Price'] = price.text.strip().replace('£', '')
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


def pagination(soup): # This function gets the next pages url. If there is no next page it returns none.
    try:
        next_page = soup.find('span', class_='s-pagination-strip')
        url = 'https://www.amazon.co.uk/' + str(next_page.find('a', class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator')['href'])
        return url
    except (AttributeError, TypeError):
        return


def saveToCSV(data, mode): # This function takes the books and uses pandas to write it to a csv file.
    df = pd.DataFrame(data)
    df.to_csv('books.csv', mode=mode, index=False, header=False)


def saveToPostgres():
    conn = psycopg2.connect('host=127.0.0.1 dbname=postgres user=postgres password=1234')
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    cur.execute('''DROP DATABASE IF EXISTS amazon''')
    cur.execute('''CREATE DATABASE amazon''')
    conn.close()

    conn = psycopg2.connect('host=127.0.0.1 dbname=amazon user=postgres password=1234')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS books (Title text, Price float, Author text, Rating text)''')
    amazon = pd.read_csv('books.csv', encoding='utf-8')
    amazon_insert = '''INSERT INTO books (Title, Price, Author, Rating, Link) VALUES (%s, %s, %s, %s, %s)'''
    for i, row in amazon.iterrows():
        cur.execute(amazon_insert, list(row))
    conn.commit()
    conn.close()


def main(): # This is the main function it is given an initial url, wipes the csv file if it already exits. It then infinitely runs the functions until the pagination function returns none.
    url = 'https://www.amazon.co.uk/s?k=data+engineering+books&crid=38DYM17O25O1K&sprefix=data+engineering+books%2Caps%2C118&ref=nb_sb_noss_1'

    saveToCSV([], 'w')
    while True:
        soup = request(url)
        data = parse(soup)
        saveToCSV(data, 'a')
        url = pagination(soup)
        if not url:
            break

    df = pd.read_csv('books.csv')
    df.drop_duplicates(subset=None, inplace=True)
    df.to_csv('books.csv', mode='w', index=False)

    saveToPostgres()


main()
