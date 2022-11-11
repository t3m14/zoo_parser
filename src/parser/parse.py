
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
            self.write_cat_to_csv()
            w_file = open("../docs/categories.csv", mode="a", encoding='utf-8')
            file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\n")
            file_writer.writerow([self.subcat_name, self.subcat_id, self.cat_id])


class ParseSubcats(BaseParser):
    def __init__(self):
        super().__init__()
        self.cats_list = []
        self.subcats_list = []
    # Собираем категории в список словарей
    async def get_cats(self):
        cats_list = []
        html = await get_html(self.start_url + "/catalog/")
        soup = BeautifulSoup(html, 'html.parser')
        cats = soup.find_all("a", {"class" : "item-depth-1"})
        for i, cat in enumerate(cats):
            cats_list.append({"cat_name" : cat.text, "cat_id" : i, "cat_obj" : cat, "subcat_url" : self.start_url + cat["href"]})
        return cats_list
    # Собираем подкатегории в список словарей, на основе категорий
    async def get_subcats(self):
        # Функция парса подкатегорий по юрлам категорий
        async def parse_subcats(url, cat):
            subcats_list = []
            html = await get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            subcats = soup.find_all("a", {"class" : "item-depth-1"})
            for i, subcat in enumerate(subcats):
                subcats_list.append({"subcat_name" : subcat.text, "subcat_id" : i, "subcat_obj" : subcat, "item_url" : self.start_url+subcat["href"], "cat" : cat})
            return subcats_list
        tasks = []
        # Ассинхронно собираем подкатегории
        for cat in self.cats_list:
            task = asyncio.create_task(parse_subcats(cat["subcat_url"], cat))
            tasks.append(task)
        await asyncio.gather(*tasks)
    # Запуск и присвоение переменным
    async def start(self):
        self.cats_list = await self.get_cats()
        self.subcats_list = await self.get_subcats()

