import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the URL to scrape
url = 'https://accordionproshop.com/collections/accesorios-acordeones'

def get_largest_image_url(data_srcset):
    """Extract the largest image URL from the data-srcset attribute."""
    images = data_srcset.split(", ")
    largest_image = images[-1].split(" ")[0]
    return largest_image

def get_product_description_and_image(product_url):
    """Fetch the product description and image from the product details page."""
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the description
    description_holder = soup.find('div', class_='easytabs-content-holder')
    description = description_holder.get_text(separator=" ", strip=True) if description_holder else "No description available"
    
    # Get the largest image URL
    img_tag = soup.find('img', class_='product-gallery__image')
    if img_tag and 'data-srcset' in img_tag.attrs:
        photo_url = "https:" + get_largest_image_url(img_tag['data-srcset'])
    elif img_tag and 'data-zoom' in img_tag.attrs:
        photo_url = "https:" + img_tag['data-zoom']
    else:
        photo_url = "No image available"
    
    return description, photo_url

# Extract category name from URL
category_name = url.rstrip('/').split('/')[-1]

# Fetch the main page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the parent container with all products
product_list = soup.find('div', class_='product-list product-list--collection product-list--with-sidebar')
if not product_list:
    print("Product list container not found")
    exit()

# Extract individual product details
products = product_list.find_all('div', class_='product-item')
if not products:
    print("No products found")
    exit()

product_data = []

for product in products:
    try:
        product_id = product.find('form').find('input', {'name': 'id'})['value']
        title = product.find('a', class_='product-item__title').text.strip()
        category = product.find('a', class_='product-item__vendor').text.strip()
        price_tag = product.find('span', class_='money')
        price = price_tag.text.strip() if price_tag else 'Price not available'

        # Extract the product link to fetch the description and image
        product_link = "https://accordionproshop.com" + product.find('a', class_='product-item__title')['href']
        description, photo_url = get_product_description_and_image(product_link)
        
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
            'Regular price': price.replace('$', '').replace('USD', '').strip(),
            'Categories': category,
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

# Check if any data was extracted
if not product_data:
    print("No product data extracted")
    exit()

# Create a DataFrame and export to CSV
df = pd.DataFrame(product_data)
file_name = f'{category_name}_products.csv'
df.to_csv(file_name, index=False)

print(f"Data exported to {file_name}")
