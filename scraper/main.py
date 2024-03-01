import requests
from bs4 import BeautifulSoup


def request(url):
    headers = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36'})
    response = requests.get(url, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        html = response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parse(soup):
    books = soup.findAll('div', class_='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16')

    for book in books:
        title = book.findAll('span', class_='a-size-medium a-color-base a-text-normal')
        price = book.findAll('span', class_='a-offscreen')
        rating = book.findAll('span', class_='a-icon-alt')
        link = book.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')[
            'href']

        try:
            print(f'Title: {title[0].get_text()}')
            print(f'Price: {price[0].get_text()}')
            print(f'RRP: {price[1].get_text()}')
            print(f'Ratings: {rating[0].get_text()}')
            print(f'Link: https://www.amazon.co.uk/{link}')
            print('\n')
        except IndexError:
            print('\n')


def pagination(soup):
    try:
        next_page = \
        soup.find('a', class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator')['href']
        url = 'https://www.amazon.co.uk/' + next_page
        return url
    except TypeError:
        print('\n')


def main():
    url = 'https://www.amazon.co.uk/s?k=data+engineering+books&crid=1NKLYJG6MVL6T&sprefix=data+engineering+book%2Caps%2C60&ref=nb_sb_noss_1'

    for i in range(20):
        soup = request(url)
        parse(soup)
        url = pagination(soup)

main()
