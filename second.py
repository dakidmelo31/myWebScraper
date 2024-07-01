import requests
from bs4 import BeautifulSoup
import pandas as pd

# Initialize the product ID counter
product_id_counter = 10000  # Starting from 10000 to avoid conflicts with existing IDs

def get_product_description_and_image_carnegieaccordion(product_url):
    """Fetch the product description and image from the product details page."""
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the description
    description_holder = soup.find('div', class_='wpb_wrapper')
    description = description_holder.get_text(separator=" ", strip=True) if description_holder else "No description available"
    
    # Get the largest image URL
    img_tag = soup.find('div', class_='product-images-big').find('img')
    if img_tag:
        photo_url = img_tag['src']
    else:
        photo_url = "No image available"
    
    return description, photo_url

def scrape_carnegieaccordion(url):
    global product_id_counter
    
    # Extract category name from URL
    category_name = url.rstrip('/').split('/')[-1]

    # Fetch the main page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the sections with all products
    product_sections = soup.find_all('section', class_='wixui-section')
    if not product_sections:
        print("Product sections not found")
        return

    product_data = []

    for section in product_sections:
        try:
            # Extract the product details from the main page
            title_tag = section.find('div', class_='HcOXKn c9GqVL QxJLC3')
            title = title_tag.text.strip()
            price = title_tag.find('span', class_='wixui-rich-text__text').text.strip()
            
            # Get the product link to fetch the description and image
            product_link = section.find('a')['href']
            description, photo_url = get_product_description_and_image_carnegieaccordion(product_link)
            
            product_id = product_id_counter
            product_id_counter += 1

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
                'Regular price': price.replace('$', '').strip(),
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

    # Check if any data was extracted
    if not product_data:
        print("No product data extracted")
        return

    # Create a DataFrame and export to CSV
    df = pd.DataFrame(product_data)
    file_name = f'{category_name}_products.csv'
    df.to_csv(file_name, index=False)

    print(f"Data exported to {file_name}")

# URL to scrape
url = 'https://www.carnegieaccordion.com/bugari-accordions'

scrape_carnegieaccordion(url)
