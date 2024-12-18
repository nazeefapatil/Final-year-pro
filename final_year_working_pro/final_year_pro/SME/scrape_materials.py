import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
from .models import RawMaterial, RawMaterialCategory, Supplier, SupplierMaterial

class RawMaterialScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()

    def setup_selenium(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    def scrape_alibaba(self, category):
        """
        Scrape raw materials from Alibaba based on category
        """
        base_url = f"https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={category}"
        driver = self.setup_selenium()
        driver.get(base_url)

        # Wait for products to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-no-v2-main"))
        )

        products = []
        items = driver.find_elements(By.CLASS_NAME, "list-no-v2-item")

        for item in items[:10]:  # Limit to first 10 items
            try:
                name = item.find_element(By.CLASS_NAME, "elements-title-normal").text
                price = item.find_element(By.CLASS_NAME, "elements-offer-price-normal").text
                supplier = item.find_element(By.CLASS_NAME, "supplier-name").text

                products.append({
                    'name': name,
                    'price': price,
                    'supplier': supplier
                })
            except Exception as e:
                print(f"Error extracting product: {e}")

        driver.quit()
        return products

    def scrape_indiamart(self, category):
        """
        Scrape raw materials from IndiaMart based on category
        """
        url = f"https://dir.indiamart.com/search.mp?ss={category}&prdsrc=1"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = []
        items = soup.find_all('div', class_='clg')

        for item in items[:10]:
            try:
                name = item.find('a', class_='prd-name').text.strip()
                supplier = item.find('span', class_='lcname').text.strip()
                location = item.find('span', class_='loc').text.strip()

                products.append({
                    'name': name,
                    'supplier': supplier,
                    'location': location
                })
            except Exception as e:
                print(f"Error extracting product: {e}")

        return products

    def save_to_database(self, products, category_name):
        try:
            category, _ = RawMaterialCategory.objects.get_or_create(category_name=category_name)

            supplier_materials_list = []  # Collect SupplierMaterial objects for bulk creation

            for product in products:
                if not product['name'] or not product['supplier']:
                    continue  # Skip invalid products

                # Create or update supplier
                supplier, _ = Supplier.objects.get_or_create(
                    company_name=product['supplier'],
                    defaults={'country': product.get('location', 'Unknown')}
                )

                # Create or update raw material
                material, _ = RawMaterial.objects.get_or_create(
                    material_name=product['name'],
                    category=category,
                    defaults={'description': f"Supplied by {product['supplier']}"}
                )

                # Create supplier material entry
                if 'price' in product:
                    try:
                        price = float(product['price'].replace('$', '').replace(',', ''))
                        supplier_material = SupplierMaterial(
                            supplier=supplier,
                            material=material,
                            current_stock=0,  # Default stock value
                            price_per_unit=price,
                            minimum_order_quantity=1,
                            available_from=timezone.now().date(),
                            available_until=timezone.now().date() + timezone.timedelta(days=30)
                        )
                        supplier_materials_list.append(supplier_material)
                    except ValueError:
                        print(f"Invalid price format for {product['name']}")

            # Bulk create supplier materials
            SupplierMaterial.objects.bulk_create(supplier_materials_list, ignore_conflicts=True)

        except Exception as e:
            print(f"Error saving to database: {e}")

    def run_scraping(self, categories):
        """
        Main method to run scraping for multiple categories
        """
        all_products = []

        for category in categories:
            print(f"Scraping category: {category}")

            # Scrape from multiple sources
            alibaba_products = self.scrape_alibaba(category)
            indiamart_products = self.scrape_indiamart(category)

            # Combine products from different sources
            category_products = alibaba_products + indiamart_products

            # Save to database
            self.save_to_database(category_products, category)

            all_products.extend(category_products)

        return all_products

# Usage example
if __name__ == "__main__":
    scraper = RawMaterialScraper()
    categories = ['spices', 'grains', 'metals', 'chemicals']
    products = scraper.run_scraping(categories)
