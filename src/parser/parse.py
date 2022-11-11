from datetime import datetime
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

class Item():
    def __init__(self):
        self.price_datetime = None
        self.price = None
        self.price_promo = None
        self.sku_status = None
        self.sku_barcode = None
        self.sku_article = None
        self.sku_name = None
        self.sku_category = None
        self.sku_country = None
        self.sku_weight_min = None
        self.sku_volume_min = None
        self.sku_quantity_min = None
        self.sku_link = None
        self.sku_images = None
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
                for i, item in enumerate(items):
                    subitems = item.parent.find_all("a", {'class' : "item-depth-3"})
                    self.items_list.append({"item_id" : i, "item_name" : item.text, "item_url" : self.start_url + item["href"], "subcat" : subcat})
                    if subitems:
                        for subitem in subitems:
                            self.items_list.append({"item_id" : i, "item_name" : item.text, "item_url" : self.start_url + item["href"], "subitem_id" : i, "subitem_name" : subitem.text, "subitem_url" : self.start_url + subitem["href"], "subcat" : subcat})
                        
    # Запуск и присвоение переменным
    async def start(self):
        await self.get_cats()
        await self.get_subcats()
        await self.get_items()
class ParseItems(BaseParser):
    def __init__(self):
        super().__init__()
        
    async def start(self):
        await self.parse_all()
    async def get_catalog_urls(self):
        catalog_urls = []
        items = ParseSubcats()
        await items.run()
        items = items.items_list
        for i in items:
            catalog_urls.append(i["subitem_url"]) if "subitem_url" in i else catalog_urls.append(i["item_url"])
        return catalog_urls
    async def parse_item(self, url):
        async def sub_parse(u):
            html = await get_html(self.start_url + u)
            soup = BeautifulSoup(html, "html.parser")

            # Цены на товар
            price = soup.find("s", {"style" : "color:#000000;"})
            if not price:
                price = soup.find("span", {"class" : "catalog-price"})
            promo_price = soup.find("span", {"class" : "catalog-price"})
            
            # Наличие
            sku_status = 0 if soup.find("div", {"class" : "catalog-item-no-stock"}) else 1
            # Баркоды
            sku_barcode = []
            sku_barcodes = soup.find_all("b", {"style" : "color:#c60505;"})
            for bar in sku_barcodes:
                if bar not in sku_barcode:
                    sku_barcode.append(bar.text)
            # Артикл
            sku_article = []
            sku_articles = soup.find_all("td", {"class" : "b-catalog-element-offer-first-col"})
            for art in sku_articles:
                if art not in sku_article:
                    sku_article.append(art.text)
            # Имя
            sku_name = soup.find("h1").text
            # Крошки
            sku_category = ""
            sku_categorys = soup.find("ul", {"class" : "breadcrumb-navigation"}).find_all("li")
            for li in sku_categorys:
                if li.text != "&nbsp;→&nbsp;":
                    sku_category += li.text+ "|"
            # Страна
            sku_country = soup.find("div", {"class" : "catalog-element-offer-left"}).text.split("Страна производства: ")[-1]
            fas = soup.find("b", {"style":"color:#000000;font-size: 22px;"}).text
            val = new_string = "".join((x for x in fas if not x.isdigit()))
            # Минимальный вес
            sku_weight_min = None
            # Минимальный объём
            sku_volume_min = None
            # Мимимальное количество
            sku_quantity_min = None
            if val in ["г", "кг"]:
                sku_weight_min = fas
            elif val in ["мл", "л", "мл."]:
                sku_volume_min = fas
            else:
                sku_quantity_min = fas
            # Ссылка на товар
            sku_link = self.start_url + u
            # Ссылка на изображение
            sku_image = []
            sku_image_wraper = soup.find("div", {"class" : "catalog-element-offer-pictures"})
            sku_images = sku_image_wraper.find_all("img", {"width" : "73"})
            for img in sku_images:
                if "/upload/" in img["src"]:
                    sku_image.append(self.start_url + img['src'])
            sku_image.append(self.start_url + sku_image_wraper.find("img", {"width" : "245"})['src'])
            # А теперь создадим новый инстанс итем
            item = Item()
            # Присвоим ему полученные значения
            item.price_datetime = datetime.now()
            item.price = price
            item.price_promo = promo_price
            item.sku_status = sku_status
            item.sku_barcode = sku_barcode
            item.sku_article = sku_article
            item.sku_name = sku_name
            item.sku_category = sku_category
            item.sku_country = sku_country
            item.sku_weight_min = sku_weight_min
            item.sku_volume_min = sku_volume_min
            item.sku_quantity_min = sku_quantity_min
            item.sku_link = sku_link
            item.sku_images = sku_images

        try:
            urls = await self.get_items_urls(url)
        except Exception as e:
            print("Ошибка с урлами")
            print(e)
            return
        
        for u in urls:
            try:
                await sub_parse(u)
            except Exception as e:
                print("Ошибка парсинга")
                print(e)
            
    async def get_items_urls(self, url):
        html = await get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.find_all("div", {"class": "catalog-content-info"})
        hrefs = []
        for div in divs:
            hrefs.append(div.find("a", {"class": "name"})['href'])
        return hrefs
    async def parse_all(self):
        urls = await self.get_catalog_urls()
        tasks = []
        for url in urls:
            # Получаем ссылки и парсим товар
            task = asyncio.create_task(self.parse_item(url))
            tasks.append(task)
        await asyncio.gather(*tasks)
        print(self.all_items_links)