from time import sleep
from utils.load_config import get_json
class BaseParser():
    # Подгружаем конфиг в конструкторе класса
    def __init__(self):
        config = get_json()
        self.output_directory = config["output_directory"]
        self.categories = config["categories"]
        self.delay_range_s = config["delay_range_s"].split("-")
        self.max_retries = config["max_retries"]
        self.headers = config["headers"]
        self.logs_dir = config["logs_dir"]
        self.restart_count = int(config["restart"]["restart_count"])
        self.interval_m = int(config["restart"]["interval_m"])
        self.start_url = "http://zootovary.ru"
        self.__restarts = 0
    # Запуск парсинга (Запускаепм скрипт, если произошла ошибка - перезапскаем)
    async def run(self):
        try:
            await self.start()
        except Exception as e:
            print(e)
            if self.__restarts <= self.restart_count:
                sleep(self.interval_m * 60)
                self.__restarts += 1
                await self.run()
    async def start():
        pass
    # Приостановить
    def pause(self):
        pass
    # Функция перезапуска
    def restart(self):
        self.run()
    # Деструктор
    def __del__(self):
        pass