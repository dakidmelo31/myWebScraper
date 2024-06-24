import requests
from bs4 import BeautifulSoup
import pandas as pd

# Initialize the product ID counter
product_id_counter = 10000  # Starting from 10000 to avoid conflicts with existing IDs

def get_product_details_goldstock(product_url):
    """Fetch the product details from the product details page."""
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the description from the table
    description_table = soup.find('table', class_='sm')
    description = ''
    if description_table:
        rows = description_table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                description += f"{cols[0].text.strip()}: {cols[1].text.strip()} "
    
    return description.strip()

def scrape_goldstock(url):
    global product_id_counter
    product_data = []
    page = 1
    
    while True:
        response = requests.get(f"{url}?page={page}")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the parent container with all products
        products = soup.find_all('div', class_='normal-product product product-box-desktop-container not-bar')
        if not products:
            break

        for product in products:
            try:
                # Extract product ID
                product_id = product['id'].split('-')[-1]

                # Extract product link
                product_link = "https://goldstockcanada.com" + product.find('a')['href']
                
                # Extract product title
                title = product.find('div', class_='name').find('b').text.strip()
                
                # Extract product price
                price_tag = product.find('div', class_='price').find('span')
                price = price_tag.text.strip() if price_tag else 'Price not available'

                # Extract image URL
                img_tag = product.find('div', class_='image').find('img')
                photo_url = "https://goldstockcanada.com" + img_tag['src'] if img_tag else "No image available"

                # Fetch the product details
                description = get_product_details_goldstock(product_link)
                
                product_data.append({
                    'ID': product_id,
                    'Type': 'simple',
                    'SKU': '',
                    'Name': title,
                    'Published': 1,
                    'Is featured?': 0,
                    'Visibility in catalog': 'visible',
                    'Short description': description[:75],  # Assuming short description is the first 75 characters of the full description
                    'Description': description,
                    'Date sale price starts': '',
                    'Date sale price ends': '',
                    'Tax status': 'taxable',
                    'Tax class': '',
                    'In stock?': 1,
                    'Stock': 1,
                    'Low stock amount': '',
                    'Backorders allowed?': 0,
                    'Sold individually?': 0,
                    'Weight (kg)': '',
                    'Length (cm)': '',
                    'Width (cm)': '',
                    'Height (cm)': '',
                    'Allow customer reviews?': 1,
                    'Purchase note': '',
                    'Sale price': '',
                    'Regular price': price.replace('CAD', '').replace('$', '').strip(),
                    'Categories': 'Gold Stock',
                    'Tags': '',
                    'Shipping class': '',
                    'Images': photo_url,
                    'Download limit': '',
                    'Download expiry days': '',
                    'Parent': '',
                    'Grouped products': '',
                    'Upsells': '',
                    'Cross-sells': '',
                    'External URL': '',
                    'Button text': '',
                    'Position': 0
                })

            except Exception as e:
                print(f"Error processing product: {e}")

        # Check for next page
        pagination = soup.find('ul', class_='pagination')
        if not pagination or not pagination.find('a', rel='next'):
            break
        page += 1

    # Check if any data was extracted
    if not product_data:
        print("No product data extracted")
        return

    # Create a DataFrame and export to CSV
    df = pd.DataFrame(product_data)
    file_name = 'item_sample_products.csv'
    df.to_csv(file_name, index=False)

    print(f"Data exported to {file_name}")

# URL to scrape
url = 'https://goldstockcanada.com/shop'
scrape_goldstock(url)
