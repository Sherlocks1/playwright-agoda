import asyncio
import logging

from setting import hotel_info
from urlgen import urlgen
from mixdata3 import crawler
from tools import clean_filename
from savedata import save_data
from tools import delete_html_files

hotel_name, hotel_id = hotel_info()

if __name__ == '__main__':
    urlgen(hotel_name, hotel_id)
    try:
        logging.info("程序开始运行")
        asyncio.run(crawler())

        # 统计爬取状态并输出
        success_files = []
        fail_files = []
        with open("urls.txt", "r") as f:
            urls = f.read().splitlines()
        for url in urls:
            filename = clean_filename(url)
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    success_files.append(filename)
            except FileNotFoundError:
                fail_files.append(filename)

        logging.info(f"程序运行完毕 - 爬取成功：{', '.join(success_files)}, 爬取失败：{', '.join(fail_files)}")

    except Exception as e:
        logging.error(f"Error: {e}")
    save_data(hotel_name)
    delete_html_files()
