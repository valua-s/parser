import logging
import requests
from time import sleep
from bs4 import BeautifulSoup
import csv

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


BASE_URL = "magbo.ru"


def search_products(query: str, region_name='') -> list:
    q_request: str = query.replace(' ', '+')
    if region_name:
        region_name += '.'
    full_url = f"https://{region_name}{BASE_URL}"
    search_url = f"{full_url}/catalog/?q={q_request}&s=Найти"
    try:
        response = requests.get(search_url)
    except Exception as e:
        logger.error(e)
        sleep(3)
    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
    try:
        pages = int(soup.select('[href*="PAGEN_2"]')[-1].text)
    except IndexError:
        pages = None
    product_links = []
    for link in soup.select('.dark_link.option-font-bold.font_sm'):
        product_links.append(link.get('href'))

    if pages:
        for page in range(2, pages+1):
            search_url += f'&PAGEN_2={page}'
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.select('.dark_link.option-font-bold.font_sm'):
                product_links.append(link.get('href'))

    return product_links


def parse_product(product_url: str, region_name: str = '') -> dict:
    if region_name:
        region_name += '.'
    full_product_url = f"https://{region_name}{BASE_URL}{product_url}"
    try:
        response = requests.get(full_product_url)
    except Exception as e:
        logger.error(e)
        sleep(3)
    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')

    title: str = soup.select_one('h1').get_text(strip=True).replace('"', '')
    price_with_discount: str = soup.select_one('.price_value_block.values_wrapper > .price_value').get_text(strip=True)
    try:
        price_without_discount: str = soup.select_one('.discount.values_wrapper.font_xs.muted > .price_value').get_text(strip=True)
    except Exception:
        price_without_discount = price_with_discount
        price_with_discount = None
    article: str = soup.select_one('.properties__value.darken.properties__item--inline.js-prop-value').get_text(strip=True)
    
    manufacturer: str = soup.find_all('span', class_='js-prop-value')[3].get_text(strip=True)
    availability: str = soup.select_one('.value.font_sxs').get_text(strip=True)
    
    return {
        'title': title,
        'price_with_discount': price_with_discount,
        'price_without_discount': price_without_discount,
        'article': article,
        'manufacturer': manufacturer,
        'availability': availability,
        'url': full_product_url,
    }


def save_to_csv(data: list, filename: str = 'products.csv') -> None:
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def main(queries: dict, region_names: dict) -> None:
    
    all_products: list = []
    
    for query in queries:
        for region_name in region_names:
            product_links: list = search_products(query, region_name)
        
            for product_link in product_links:
                product_data: dict = parse_product(product_link, region_name)
                all_products.append(product_data)
    
    save_to_csv(all_products)


if __name__ == "__main__":
    queries: list = ["Биде Sole", "Смеситель Kerama Marazzi"]
    # all_region_names = ['bahchisarai', 'evpatoria', 'kerch', 'saki', 'sevastopol', '', 'feodosia', 'yalta']
    main(queries,)
