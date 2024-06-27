import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import random
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_soup(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure we notice bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching the URL: {url} - {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def scrape_gallery_images(iframe_url):
    gallery_images = []
    soup = get_soup(iframe_url)
    if soup:
        images = soup.find_all('img')
        gallery_images = [img['src'] for img in images if 'src' in img.attrs]
    return gallery_images

def scrape_products(base_url):
    products = []
    page = 1

    while True:
        logging.info(f"Scraping page {page}...")
        soup = get_soup(f"{base_url}?page={page}")
        if soup is None:
            break
        
        product_cards = soup.select('div[data-testid="richTextElement"]')
        if not product_cards:
            break  # Exit if no products found
        
        for card in product_cards:
            try:
                title_element = card.select_one('span[style="font-weight:bold; font-size:44px;"]')
                description_element = card.select_one('span[style="font-size:22px; font-weight:bold;"]')
                image_tag = card.select_one('img')
                
                if title_element and description_element and image_tag:
                    title = title_element.text.strip()
                    description = description_element.text.strip()
                    image_url = image_tag['src']
                    iframe = card.find_next('iframe')
                    iframe_url = iframe['src'] if iframe else None
                    gallery_images = scrape_gallery_images(iframe_url) if iframe_url else []
                    
                    products.append({
                        'Name': title,
                        'Description': description,
                        'SKU': title.replace(' ', '_').lower(),
                        'Price': str(random.randint(2500, 12150)),
                        'Stock': 'instock',
                        'Image': image_url,
                        'Gallery': ','.join(gallery_images),
                        'Specifications': ""  # Assuming no additional specifications for simplicity
                    })
            except Exception as e:
                logging.error(f"Error parsing product card: {e}")
        
        pagination = soup.select_one('nav.pagination')
        if not pagination or not pagination.select_one('a.button'):
            break  # Exit if no more pages
        
        page += 1
        time.sleep(1)  # Respectful scraping

    return products

def save_to_csv(products, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'ID', 'Type', 'SKU', 'Name', 'Published', 'Is featured?', 
            'Visibility in catalog', 'Short description', 'Description', 
            'Date sale price starts', 'Date sale price ends', 'Tax status', 
            'Tax class', 'In stock?', 'Stock', 'Low stock amount', 
            'Backorders allowed?', 'Sold individually?', 'Weight (kg)', 
            'Length (cm)', 'Width (cm)', 'Height (cm)', 
            'Allow customer reviews?', 'Purchase note', 'Sale price', 
            'Regular price', 'Categories', 'Tags', 'Shipping class', 
            'Images', 'Gallery', 'Download limit', 'Download expiry days', 
            'Parent', 'Grouped products', 'Upsells', 'Cross-sells', 
            'External URL', 'Button text', 'Position', 'Meta: _custom_type', 
            'Meta: _material', 'Meta: _color', 'Meta: _size', 'Meta: _style'
        ]
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
                'Categories': 'Accordion Products',
                'Images': product['Image'],
                'Gallery': product['Gallery']
            })

if __name__ == "__main__":
    base_url = "https://carnegieaccordion.com/solloni"
    products = scrape_products(base_url)
    save_to_csv(products, 'product_sample_accordions.csv')
    logging.info("Scraping complete. CSV file generated.")
