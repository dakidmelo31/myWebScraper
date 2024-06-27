import requests
from bs4 import BeautifulSoup
import csv
import time

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {url} - {e}")
        return None

def scrape_products(url):
    products = []
    page = 1

    while True:
        print(f"Scraping page {page}...")
        soup = get_soup(f"{url}?page={page}")
        if soup is None:
            break
        
        product_cards = soup.find_all('li', class_='listing-results__item')
        if not product_cards:
            break  # Exit if no products found
        
        for card in product_cards:
            try:
                title_tag = card.find('p', class_='product-card__title').find('a')
                title = title_tag.text.strip()
                product_url = title_tag['href']
                price = card.find('strong', class_='product-card__strongtext js-lp-price').text.strip()
                image_url = card.find('picture', class_='product-card__image').find('img')['data-src']
                description, specifications, gallery_images = scrape_product_details(f"https://atkinsonsbullion.com{product_url}")
                
                products.append({
                    'Name': title,
                    'Description': description,
                    'SKU': product_url.split('/')[-1],
                    'Price': price.replace('£', ''),
                    'Stock': 'instock',
                    'Image': image_url,
                    'Gallery': ','.join(gallery_images),
                    'Specifications': specifications
                })
            except Exception as e:
                print(f"Error parsing product card: {e}")
        
        pagination = soup.find('nav', class_='pagination')
        if not pagination or not pagination.find('a', class_='button'):
            break  # Exit if no more pages
        
        page += 1
        time.sleep(1)  # Respectful scraping

    return products

def scrape_product_details(url):
    soup = get_soup(url)
    if soup is None:
        return "", "", []

    description_div = soup.find('div', class_='tab__content-inner', id='s0-inner')
    description = description_div.text.strip() if description_div else ""

    specifications_div = soup.find('div', class_='tab__content-inner', id='s1-inner')
    specifications = specifications_div.find('table').text.strip() if specifications_div else ""

    gallery_images = []
    gallery_container = soup.find('div', class_='product-gallery__main-container')
    if gallery_container:
        image_tags = gallery_container.find_all('img', class_='product-card__image')
        gallery_images = [img['src'] for img in image_tags]

    return description, specifications, gallery_images

def save_to_csv(products, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Type', 'SKU', 'Name', 'Published', 'Is featured?', 'Visibility in catalog', 'Short description', 'Description', 'Date sale price starts', 'Date sale price ends', 'Tax status', 'Tax class', 'In stock?', 'Stock', 'Low stock amount', 'Backorders allowed?', 'Sold individually?', 'Weight (kg)', 'Length (cm)', 'Width (cm)', 'Height (cm)', 'Allow customer reviews?', 'Purchase note', 'Sale price', 'Regular price', 'Categories', 'Tags', 'Shipping class', 'Images', 'Gallery', 'Download limit', 'Download expiry days', 'Parent', 'Grouped products', 'Upsells', 'Cross-sells', 'External URL', 'Button text', 'Position', 'Meta: _custom_type', 'Meta: _material', 'Meta: _color', 'Meta: _size', 'Meta: _style']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for index, product in enumerate(products, start=1):
            writer.writerow({
                'ID': index,
                'Type': 'simple',
                'SKU': product['SKU'],
                'Name': product['Name'],
                'Published': 1,
                'Is featured?': 0,
                'Visibility in catalog': 'visible',
                'Short description': product['Description'],
                'Description': product['Specifications'],
                'Tax status': 'taxable',
                'In stock?': 1,
                'Stock': product['Stock'],
                'Regular price': product['Price'],
                'Categories': 'Gold Coins',
                'Images': product['Image'],
                'Gallery': product['Gallery']
            })

if __name__ == "__main__":
    url = "https://atkinsonsbullion.com/gold/gold-coins"
    products = scrape_products(url)
    save_to_csv(products, 'product_sample_coins.csv')
    print("Scraping complete. CSV file generated.")
