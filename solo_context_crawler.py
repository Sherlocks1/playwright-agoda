# -*- coding = utf-8 -*-
# @Time : 2023/4/3 0:13
# @Author : Sherlock
# @File : crawler.py
# @Software : PyCharm

import asyncio
import logging

from playwright.async_api import async_playwright

from tools import clean_filename
from tools import random_wait
from get_data import get_data
from fake_useragent import UserAgent
from settings import HEADLESS, MAX_CONCURRENT_TASKS, MAX_RETRIES, TIMEOUT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("my_log_file.log"),
        logging.StreamHandler(),
    ],
)


async def crawler():
    # 打开存储 URL 的文件
    with open("urls.txt", "r") as f:
        urls = f.read().splitlines()

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=HEADLESS)

        tasks = []

        max_concurrent_tasks = MAX_CONCURRENT_TASKS  # 控制同时执行的任务数量
        current_task_count = 0  # 当前正在执行的任务数

        for i in range(len(urls)):
            if current_task_count >= max_concurrent_tasks:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for completed_task in done:
                    try:
                        await completed_task
                        tasks.remove(completed_task)
                        current_task_count -= 1
                    except Exception as error:
                        logging.error(f"Error while running task: {error}")

            context = await browser.new_context()

            js = """
            Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
            """
            await context.add_init_script(js)

            # 设置页面默认超时时间
            context.set_default_timeout(TIMEOUT)

            page = await context.new_page()
            page.set_default_timeout(TIMEOUT)

            task_name = f"Task {i + 1}"
            filename = clean_filename(urls[i])

            # 设置页面headers
            ua = UserAgent(browsers=["edge", "chrome", "internet explorer", "firefox", "safari", "opera"])
            headers = {'User-Agent': ua.random}

            task = asyncio.create_task(
                get_data(page, urls[i], filename, max_retries=MAX_RETRIES,
                         task_name=task_name, headers=headers))

            cookies = await context.cookies()
            print(cookies)

            await random_wait()

            tasks.append(task)
            current_task_count += 1

        # 使用 asyncio.as_completed() 按完成顺序等待任务的完成
        for completed_task in asyncio.as_completed(tasks):
            try:
                await completed_task
                tasks.remove(completed_task)
                current_task_count -= 1
            except Exception as error:
                logging.error(f"Error while running task: {error}")



        await browser.close()


if __name__ == '__main__':
    try:
        logging.info("程序开始运行")
        asyncio.run(crawler())

    except Exception as e:
        logging.error(f"Error: {e}")
