import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import pandas as pd  # pip install pandas
import psycopg2  # pip install psycopg2


def request(url, session):  # This function sends a request to the url that is provided and returns a soup object with the web pages html.
    response = session.get(url)  # Creates a single session with the given URL.
    print(response.status_code)  # response of <200> indicates a successful connection.
    soup = BeautifulSoup(response.text, 'html.parser')  # Creates a soup object of the html retrieved from the URL.
    return soup  # returns the soup object.


def parse(soup):  # This function finds every book on the web page and parses through and extracts the information. It returns the books in a list.

    books = soup.findAll('div', class_='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16')  # Finds all books on the page.
    print(len(books))
    data = []
    for book in books:  # loops through to parse every book found on the page.
        item = {}
        try:
            title = book.find('span', class_='a-size-medium a-color-base a-text-normal')  # Finds the Title of the book
            if title:  # IF the Title is found
                item['Title'] = title.text.strip().replace('′', '')  # Store the Title in the item dictionary, apply some string manipulation like strip, to remove whitespaces.
            else:  # IF the Title is not found.
                continue  # the Title is an essential data point, if it is missing we move onto the next book in the list of books.

            price = book.find('span', class_='a-offscreen')  # Finds the Price of the book
            if price and price.text.strip() != '£0.00':  # IF the Price is found and the price does not equal $0
                item['Price'] = price.text.strip().replace('£', '')  # We remove the £ symbol, whitespaces and then store the Price in the item dictionary.
            else:  # IF the Price is not found.
                continue  # the Price is an essential data point, if it is missing we move onto the next book in the list of books.

            author = book.find('a', class_='a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style')  # Finds the Author of the book.
            if author:  # If the Author is found.
                item['Author'] = author.text.strip()  # Remove whitespaces and then store the Author into the item dictionary.
            else:  # IF the Author is not found
                item['Author'] = 'No Author'  # The placeholder 'No Author' is used. This is a non-essential data point. So we don't need to skip parsing the book with this missing field.

            """
            The same preprocessing is done for the rest of the non-essential data points. IF the data is found for that field it is used,
            but if the data is not found for that field the corresponding placeholder is used instead.
            """

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
        data.append(item)  # Appends the data stores in the item dictionary for that specific book into the list.
    return data  # Function returns the list of every book and its data available on that web page.


def pagination(soup):  # This function gets the next pages url. If there is no next page it returns none

    page = soup.find('span', class_='s-pagination-strip')  # This finds the next page strip that is visible at the bottom of the screen.

    if page and not page.find('span', class_='s-pagination-item s-pagination-next s-pagination-disabled'):  # IF the next page strip is found and the next page button is NOT disabled.
        next_page = page.find('a', class_='s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator')  # html for the next page button is extracted.
        if next_page:  # IF the html for the next page button is extracted
            url = 'https://www.amazon.co.uk' + next_page.get('href')  # get the 'href' attribute of the htm. We concatenate the base url with the 'href' attribute to construct a complete URL for the next page.
            return url   # returns the URL for the next page.
        else:  # IF the html for the next page button is no found.
            return  # return nothing
    else:  # IF the next page strip is not found or the next page button is disabled.
        return  # return nothing


def saveToCSV(data, mode):  # This function takes the books and uses pandas to write it to a csv file.
    df = pd.DataFrame(data)  # converts the list full of books into a pandas data frame.
    df.to_csv('books.csv', mode=mode, index=False, header=False)  # use pandas built-in function to store the books into a csv file called 'books'.


def saveToPostgres():  # This function create a connection to PostgreSQL database, and stores the data from the 'books.csv' file into it.
    conn = psycopg2.connect('host=127.0.0.1 dbname=postgres user=postgres password=1234')
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    cur.execute('''DROP DATABASE IF EXISTS amazon''')  # IF the 'amazon' database already exists within the PostgreSQL database we want to delete it.
    cur.execute('''CREATE DATABASE amazon''')  # Create a database called 'amazon'
    conn.close()

    conn = psycopg2.connect('host=127.0.0.1 dbname=amazon user=postgres password=1234')  # create a connection to the 'amazon' database.
    cur = conn.cursor()

    # Creates a table called 'books' inside the 'amazon' database, with the columns of the data being extracted and their datatypes.
    cur.execute('''CREATE TABLE IF NOT EXISTS books (Title varchar, Price float, Author varchar, Rating varchar, Link text)''')

    amazon = pd.read_csv('books.csv')  # uses pandas build in function to read the contents of the 'books.csv' file.

    amazon_insert = '''INSERT INTO books (Title, Price, Author, Rating, Link) VALUES (%s, %s, %s, %s, %s)'''  #  This is creating a variable which will insert the data into the 'books' database when it is called.

    # This for loop is used to iterate over every row inside the 'books.csv' file
    # It calls the amazon_insert variable and provides all the columns of that row that will be inserted.
    for i, row in amazon.iterrows():
        cur.execute(amazon_insert, list(row))
    conn.commit()  # once the for loop is complete, it commits any changes made to the database straight away.
    conn.close()  # The connection is closed so the database cannot be modified further.


def main():  # This is the main function it is given an initial url, wipes the csv file if it already exits. It then infinitely runs the functions until the pagination function returns none.
    url = 'https://www.amazon.co.uk/s?k=data+engineering+books&crid=38DYM17O25O1K&sprefix=data+engineering+books%2Caps%2C118&ref=nb_sb_noss_1'  # This is the initial url, it searches for 'data engineering books' on amazon.

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}  # This is my user-agent, it is used to mimic a legitimate browser request.
    session = requests.Session()  # A single session is maintained to prevent overloading the server with requests from multiple 'connections'
    session.headers.update(headers)  # our user agent is provided into the single session we are going to maintain throughout the scrape.

    saveToCSV([], 'w')  # this wipes the 'books.csv' file if it already exists in the directory.

    # This is an infinite loop, it will run until no url is returned from the pagination function.
    while True:
        soup = request(url, session)  # creates our soup object
        data = parse(soup)  # retrieves a list full of data for each book on a web page.
        saveToCSV(data, 'a')  # writes the list full of data for each book into a .csv file.
        url = pagination(soup)  # finds the next page
        if not url:  # IF the url is invalid
            break  # Break out of the loop

        # else run the loop again
        print(url)

    # This checks to see if there are any duplicates within the .csv file.
    # IF a duplicate is found it is removed from the .csv file before storing it into the Postgres database.
    df = pd.read_csv('books.csv')
    df.drop_duplicates(subset=None, inplace=True)
    df.to_csv('books.csv', mode='w', index=False)

    saveToPostgres()  # Finally once every page has been scraped, this function is called to read the full processed 'books.csv' file and store it into the PostgreSQL database.


main()
