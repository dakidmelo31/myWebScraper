import requests
from bs4 import BeautifulSoup
import json
import time
import random
import mysql.connector

# Define headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Connection': 'keep-alive',
}

# Establish MySQL database connection
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='dakid',
        password='dakid',
        database='cryptomarketing'
    )

# Create the products table
def create_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        pid INT AUTO_INCREMENT PRIMARY KEY,
                        image TEXT NOT NULL,
                        title TEXT NOT NULL,
                        cost TEXT NOT NULL
                    )''')

# Get product data from the search results page
def get_product_data(result):
    try:
        title = result.find('span', class_='a-size-medium a-color-base a-text-normal').get_text(strip=True)
    except AttributeError:
        title = None

    try:
        cost = result.find('span', class_='a-price-whole').get_text(strip=True)
        cost_fraction = result.find('span', class_='a-price-fraction').get_text(strip=True)
        cost = cost + cost_fraction
    except AttributeError:
        cost = None

    try:
        image = result.find('img', class_='s-image')['src']
    except (AttributeError, TypeError):
        image = None

    product_data = {
        'title': title,
        'cost': cost,
        'image': image
    }

    return product_data

# Main function to scrape and store data
def main():
    base_url = 'https://www.amazon.com/s?k=carpet&page={}'
    products = []

    db = connect_db()
    cursor = db.cursor()
    create_table(cursor)

    for page in range(1, 21):  # Adjust the range to get the required number of products
        url = base_url.format(page)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        search_results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for result in search_results:
            product_data = get_product_data(result)

            if product_data['title'] and product_data['cost'] and product_data['image']:
                products.append(product_data)
                cursor.execute("INSERT INTO products (image, title, cost) VALUES (%s, %s, %s)",
                               (product_data['image'], product_data['title'], product_data['cost']))
                db.commit()

            # Add a delay to prevent getting blocked
            time.sleep(random.uniform(1, 3))

            if len(products) >= 200:
                break

        if len(products) >= 200:
            break

        # Add a delay between page requests to prevent getting blocked
        time.sleep(random.uniform(2, 5))

    cursor.close()
    db.close()

    print(json.dumps(products, indent=4))

if __name__ == '__main__':
    main()
