import re
import logging
import asyncio
import random
from asyncio import Queue

from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("my_log_file.log"), logging.StreamHandler()],
)


def clean_filename(url: str) -> str:
    match = re.search(r"checkIn=(\d{4}-\d{2}-\d{1,2})", url)
    if match:
        filename = match.group(1) + ".html"
    else:
        filename = "unknown.html"
    return filename


async def get_data(page, url, filename, max_retries, task_name=None):
    logging.info(f"{task_name} 开始爬取：{filename}")
    page1 = None
    retries = 0

    while True:
        try:
            await page.goto(url)

            # 等待 AGD-logo 出现
            agd_logo = await page.wait_for_selector(
                "div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']", timeout=20000
            )
            # 随机等待一段时间
            await asyncio.sleep(random.uniform(1.0, 3.0))

            # 单击 AGD-logo
            await agd_logo.click()

            # 等待新窗口打开
            async with page.expect_popup(timeout=180000) as page1_info:
                page1 = await page1_info.value
                await page.close()
                break

        except Exception as e:

            logging.error(f"{task_name} - {filename}: Error - {e}")
            logging.info(
                f"{task_name} - {filename}: Etrip页第 {retries + 1} 次等待元素超时！尝试重新加载"
            )
            if retries == max_retries:
                logging.info(
                    f"{task_name} - {filename}: Etrip页达到最大重试次数,爬取失败"
                )
                await page.close()
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    async with page1:
        await page1.goto(page1.url)

        page2 = None
        retries = 0

        async with page1.expect_popup(timeout=180000) as page2_info:
            while True:
                try:

                    # 等待链接出现
                    link = await page1.wait_for_selector(
                        'xpath=/html[1]/body[1]/div[11]/div[1]/div[3]/div[1]/div[1]/div[2]/div[1]/div[3]/ol[1]/li['
                        '1]/div[2]/a[1]/div[1]/div[3]/div[1]',
                        timeout=40000,
                    )

                    # 随机等待一段时间
                    await asyncio.sleep(random.uniform(1.0, 3.0))

                    # 单击链接
                    await link.click()

                    page2 = await page2_info.value

                    # 成功打开 page2 后关闭 page1 页面
                    await page1.close()

                    break
                except Exception as e:
                    logging.error(f"{task_name} - {filename}: Error - {e}")
                    logging.info(
                        f"{task_name} - {filename}Agoda列表页第 {retries + 1} 次等待元素超时！尝试重新加载"
                    )
                    if retries == max_retries:
                        logging.info(
                            f"{task_name} - {filename}: Agoda列表页达到最大重试次数,爬取失败"
                        )
                        await page1.close()
                        return  # 达到最大重试次数，退出程序
                    else:
                        # 刷新页面，并递增计数器
                        await page1.reload()
                        retries += 1

                    async with page2:
                        await page2.goto(page2.url)

                        retries = 0
                        while True:
                            try:

                                # 等待元素加载完成
                                await page2.wait_for_selector(
                                    "//*[@id='roomGrid']", timeout=20000
                                )

                                html = await page2.content()

                                with open(filename, "w", encoding="utf-8") as f:
                                    f.write(html)

                                logging.info(f"{task_name} - {filename}: 爬取成功")

                                # 随机等待一段时间
                                await asyncio.sleep(random.uniform(1.0, 3.0))

                                await page2.close()
                                break

                            except Exception as e:
                                logging.error(f"Error: {e}")
                                logging.info(
                                    f"{task_name} - {filename}酒店页第 {retries + 1} 次等待元素超时！尝试重新加载"
                                )
                                if retries == max_retries:
                                    logging.info(
                                        f"{task_name} - {filename}酒店页达到最大重试次数,爬取失败"
                                    )
                                    return  # 达到最大重试次数，退出程序
                                else:
                                    # 刷新页面，并递增计数器
                                    await page2.reload()
                                    retries += 1


async def process_queue(queue, context, max_retries, task_name_prefix):
    while True:
        url = await queue.get()
        task_name = f"{task_name_prefix} - Task {queue.qsize() + 1}"
        filename = clean_filename(url)
        page = await context.new_page()
        page.set_default_timeout(180000)
        await get_data(page, url, filename, max_retries, task_name)
        await page.context.close()


async def main():
    # 打开存储 URL 的文件
    with open("urls.txt", "r") as f:
        urls = f.read().splitlines()

    async with async_playwright() as p:
        logging.info("Launching browser")

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 设置页面默认超时时间为180秒
        context.set_default_timeout(180000)

        task_queue = Queue()
        await asyncio.gather(*[task_queue.put(url) for url in urls])

        MAX_CONCURRENT_TASKS = int(input("请设置最大运行任务数："))  # 请求用户输入并将其转换为整数 # 控制同时执行的任务数量
        max_retries = int(
            input("请设置最大重试次数：")
        )  # 请求用户输入并将其转换为整数 # 控制同时执行的任务数量

        task_name_prefix = "Agoda Scraper"

        tasks = [
            asyncio.create_task(process_queue(task_queue, context, max_retries, task_name_prefix))
            for _ in range(MAX_CONCURRENT_TASKS)
        ]

        # 等待所有任务完成
        await asyncio.gather(*tasks)

        await browser.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error: {e}")
