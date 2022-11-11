from ast import Sub
from utils.load_config import get_json
from parser.parse import *
import asyncio
async def write_cats_to_csv():
    parse = ParseSubcats()
    await parse.run()
    subcats = parse.subcats_list
    last_cat = -1
    for subcat in subcats:
        sc = Subcategory(subcat['cat']['cat_id'], subcat['subcat_id'], subcat["cat"]['cat_name'], subcat["subcat_name"])
        if last_cat != subcat['cat']['cat_id']:
            sc.write_cat_to_csv()
            last_cat = subcat['cat']['cat_id']
        sc.write_subcat_to_csv()
async def main():
    await ParseItems().run()
    
if __name__ == "__main__":
    asyncio.run(main())