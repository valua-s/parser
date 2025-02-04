import requests
from time import sleep
from bs4 import BeautifulSoup
import csv


class Parcer:
    
    def __init__(self):
        self.BASE_URL = "magbo.ru"


    def search_products(self, query, region_name=''):
        q_set = query.split(' ')
        q_request = q_set[0]
        for q in q_set[1:]:
            q_request += f'+{q}'
        if region_name:
            region_name += '.'
        self.BASE_URL = f"https://{region_name}{self.BASE_URL}"
        search_url = f"{self.BASE_URL}/catalog/?q={q_request}&s=Найти"

        response = requests.get(search_url)
        sleep(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # pages = int(soup.select('[href*="PAGEN_2"]')[-1].text)
        
        product_links = []
        
        for link in soup.select('.dark_link.option-font-bold.font_sm'):
            product_links.append(link.get('href'))
            
        # if pages:
        #     for page in range(2, pages+1):
        #         search_url += f'&PAGEN_2={page}'
        #         response = requests.get(search_url)
        #         soup = BeautifulSoup(response.text, 'html.parser')
        #         for link in soup.select('.dark_link.option-font-bold.font_sm'):
        #             product_links.append(link.get('href'))
        
        return product_links

    def parse_product(self, product_url: str):
        
        full_product_url = f'{self.BASE_URL}/{product_url}'
        response = requests.get(full_product_url)
        sleep(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.select_one('h1').get_text(strip=True).replace('"', '')
        price_with_discount = soup.select_one('.price_value_block.values_wrapper > .price_value').get_text(strip=True)
        try:
            price_without_discount = soup.select_one('.discount.values_wrapper.font_xs.muted > .price_value').get_text(strip=True)
        except Exception:
            price_without_discount = price_with_discount
            price_with_discount = None
        article = soup.select_one('.properties__value.darken.properties__item--inline.js-prop-value').get_text(strip=True)
        
        manufacturer = soup.find_all('span', class_='js-prop-value')[3].get_text(strip=True)
        availability = soup.select_one('.value.font_sxs').get_text(strip=True)
        
        return {
            'title': title,
            'price_with_discount': price_with_discount,
            'price_without_discount': price_without_discount,
            'article': article,
            'manufacturer': manufacturer,
            'availability': availability,
            'url': full_product_url,
        }

    def save_to_csv(data: list, filename='products.csv'):
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def main(self, queries: dict, region_names: dict):
        all_products = []
        
        for query in queries:
            for region_name in region_names:
                product_links = self.search_products(query, region_name)
            
                for product_link in product_links:
                    product_data = self.parse_product(product_link)
                    all_products.append(product_data)
        
        self.save_to_csv(all_products)


if __name__ == "__main__":
    queries = ["Смеситель Kerama Marazzi", "Биде Sole"]
    region_names = ['']
    # region_names = ['bahchisarai', 'evpatoria', 'kerch', 'saki', 'sevastopol', '', 'feodosia', 'yalta']
    Parcer().main(queries, region_names)
    
