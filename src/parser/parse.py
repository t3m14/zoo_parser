from cgitb import html, text
from re import sub
from bs4 import BeautifulSoup
from utils.async_request import get_html
from .parser import BaseParser
import asyncio
import csv
class Category():
    def __init__(self, cat_id, cat_name):
        self.cat_id = cat_id
        self.cat_name = cat_name
    def write_cat_to_csv(self):
        w_file = open("../docs/categories.csv", mode="a", encoding='utf-8')
        file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\n")
        file_writer.writerow([self.cat_name, self.cat_id])
class Subcategory(Category):
        def __init__(self, cat_id, subcat_id, cat_name, subcat_name):
             super().__init__(cat_id, cat_name)
             self.subcat_id = subcat_id
             self.subcat_name = subcat_name
        def write_subcat_to_csv(self):
            w_file = open("../docs/categories.csv", mode="a", encoding='utf-8')
            file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\n")
            file_writer.writerow([self.subcat_name, self.subcat_id, self.cat_id])


class ParseSubcats(BaseParser):
    def __init__(self):
        super().__init__()
        self.cats_list = []
        self.subcats_list = []
        self.items_list = []
    # Собираем категории в список словарей
    async def get_cats(self):
        html = await get_html(self.start_url + "/catalog/")
        soup = BeautifulSoup(html, 'html.parser')
        cats = soup.find_all("a", {"class" : "item-depth-1"})
        for i, cat in enumerate(cats):
            self.cats_list.append({"cat_name" : cat.text, "cat_id" : i, "cat_obj" : cat, "subcat_url" : self.start_url + cat["href"]})
    # Собираем подкатегории в список словарей, на основе категорий
    async def get_subcats(self):
        # Функция парса подкатегорий по юрлам категорий
        async def parse_subcats(url, cat):
            html = await get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            subcats = soup.find_all("a", {"class" : "item-depth-1"})
            for i, subcat in enumerate(subcats):
                self.subcats_list.append({"subcat_name" : subcat.text, "subcat_id" : i, "subcat_obj" : subcat, "item_url" : self.start_url+subcat["href"], "cat" : cat})
        tasks = []
        # Ассинхронно собираем подкатегории
        for cat in self.cats_list:
            task = asyncio.create_task(parse_subcats(cat["subcat_url"], cat))
            tasks.append(task)
        await asyncio.gather(*tasks)
    async def get_items(self):
        last_url = ''
        for subcat in self.subcats_list:
            url = subcat["cat"]["subcat_url"]
            if last_url != url:
                last_url = url
                html = await get_html(url)
                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("a", {"class" : "item-depth-2"})
                for item in items:
                    subitems = item.find_all("a", {'class' : "item-depth-3"})
                    print(item.text)
                    if subitems:
                        for subitem in subitems:
                            print(subitem.text)
                        
    # Запуск и присвоение переменным
    async def start(self):
        await self.get_cats()
        await self.get_subcats()

class ParseItems(BaseParser):
    def __init__(self):
        super().__init__()
        self.price_datetime = None
        self.price = None
        self.price_promo = None
        self.sku_status = None
        self.sku_barcode = None
        self.sku_article = None
        self.sku_name = None
        self.sku_category = None
        self.sku_country = None
        self.ksu_weight_min = None
        self.sku_volume_min = None
        self.sku_quantity_min = None
        self.sku_link = None
        self.sku_images = None
    async def start(self):
        self.get_items()
    async def get_cats():
        pass
    async def get_subcats():
        pass
    async def get_items():
        pass
    async def get_subitems():
        pass

