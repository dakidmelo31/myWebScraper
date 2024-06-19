import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_largest_image_url(data_srcset):
    """Extract the largest image URL from the data-srcset attribute."""
    images = data_srcset.split(", ")
    largest_image = images[-1].split(" ")[0]
    return largest_image

def get_product_description_and_image_accordionproshop(product_url):
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

def get_product_description_and_image_accordionshop(product_url):
    """Fetch the product description and image from the product details page."""
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the description
    description_holder = soup.find('div', class_='col-xs-12 col-sm-12 col-md-8 col-lg-6 content-col')
    description = description_holder.get_text(separator=" ", strip=True) if description_holder else "No description available"
    
    # Get the largest image URL
    img_tag = soup.find('div', class_='product-images-big').find('img')
    if img_tag:
        photo_url = img_tag['src']
    else:
        photo_url = "No image available"
    
    return description, photo_url

def scrape_accordionproshop(url):
    # Extract category name from URL
    category_name = url.rstrip('/').split('/')[-1]

    # Fetch the main page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the parent container with all products
    product_list = soup.find('div', class_='product-list product-list--collection product-list--with-sidebar')
    if not product_list:
        print("Product list container not found")
        return

    # Extract individual product details
    products = product_list.find_all('div', class_='product-item')
    if not products:
        print("No products found")
        return

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
            description, photo_url = get_product_description_and_image_accordionproshop(product_link)
            
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
        return

    # Create a DataFrame and export to CSV
    df = pd.DataFrame(product_data)
    file_name = f'{category_name}_products.csv'
    df.to_csv(file_name, index=False)

    print(f"Data exported to {file_name}")

def scrape_accordionshop(base_url):
    # Extract category name from URL
    category_name = base_url.rstrip('/').split('/')[-1]

    product_data = []
    page = 1
    while True:
        url = f"{base_url}?sf_paged={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the parent container with all products
        products = soup.find_all('div', class_='product-loop col-xs-12 col-sm-6 col-md-4 col-lg-3 item')
        if not products:
            break

        for product in products:
            try:
                product_link = product.find('a', class_='product-item')['href']
                title = product.find('h2').text.strip()
                price_tag = product.find('p', class_='price')
                price = price_tag.text.strip() if price_tag else 'Price not available'

                # Extract the product link to fetch the description and image
                description, photo_url = get_product_description_and_image_accordionshop(product_link)
                
                product_data.append({
                    'ID': '',
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
                    'Regular price': price.replace('£', '').strip(),
                    'Categories': category_name,
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
    file_name = f'{category_name}_products.csv'
    df.to_csv(file_name, index=False)

    print(f"Data exported to {file_name}")

# URLs to scrape
urls = [
    'https://accordionproshop.com/collections/anacleto',
    'https://theaccordionshop.co.uk/accordions'
]

for url in urls:
    if 'accordionproshop' in url:
        scrape_accordionproshop(url)
    elif 'theaccordionshop' in url:
        scrape_accordionshop(url)
