import re
import logging
import asyncio
import random
import aiofiles
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("my_log_file.log"),
        logging.StreamHandler(),
    ],
)


def clean_filename(url: str) -> str:
    match = re.search(r'checkIn=(\d{4}-\d{2}-\d{1,2})', url)
    if match:
        filename = match.group(1) + ".html"
    else:
        filename = "unknown.html"
    return filename


async def random_wait(min_time=1.0, max_time=3.0):
    seconds = random.uniform(min_time, max_time)
    # logging.info(f"{task_name}{filename}随机等待 {seconds:.2f} 秒")
    await asyncio.sleep(seconds)


async def get_data(page, url, filename, max_retries, task_name=None):
    logging.info(f"{task_name} 开始爬取：{filename}")
    page1 = None
    retries = 0

    Etrip_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41",
        "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8,zh-CN;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    }

    while True:
        try:
            await page.set_extra_http_headers(Etrip_headers)

            await page.goto(url)

            # 等待 AGD-logo 出现
            agd_logo = await page.wait_for_selector("div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']",
                                                    timeout=20000)
            # 随机等待一段时间
            await random_wait()

            # 单击 AGD-logo
            await agd_logo.click()

            # 等待新窗口打开
            async with page.expect_popup(timeout=120000) as page1_info:
                page1 = await page1_info.value
                await page.close()
                break

        except Exception as e:

            logging.error(f"{task_name} - {filename}: Error - {e}")
            logging.info(f"{task_name} - {filename}: Etrip页第 {retries + 1} 次等待元素超时！尝试重新加载")
            if retries == max_retries:
                logging.warning(f"{task_name} - {filename}: Etrip页达到最大重试次数,爬取失败")
                await page.close()
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    async with page1:

        Agodalist_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/90.0.4430.212 Safari/537.36",
            "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8,zh-CN;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
        }

        await page1.set_extra_http_headers(Agodalist_headers)
        await page1.goto(page1.url)

        page2 = None
        retries = 0

        async with page1.expect_popup(timeout=120000) as page2_info:
            while True:
                try:

                    # 等待链接出现
                    link = await page1.wait_for_selector(
                        'xpath=/html[1]/body[1]/div[11]/div[1]/div[3]/div[1]/div[1]/div[2]/div[1]/div[3]/ol[1]/li['
                        '1]/div[2]/a[1]/div[1]/div[3]/div[1]',
                        timeout=40000)

                    # 随机等待一段时间
                    await random_wait()

                    # 单击链接
                    await link.click()

                    page2 = await page2_info.value

                    # 成功打开 page2 后关闭 page1 页面
                    await page1.close()

                    break
                except Exception as e:
                    logging.error(f"{task_name} - {filename}: Error - {e}")
                    logging.info(f"{task_name} - {filename}Agoda列表页第 {retries + 1} 次等待元素超时！尝试重新加载")
                    if retries == max_retries:
                        logging.warning(f"{task_name} - {filename}: Agoda列表页达到最大重试次数,爬取失败")
                        await page1.close()
                        return  # 达到最大重试次数，退出程序
                    else:
                        # 刷新页面，并递增计数器
                        await page1.reload()
                        retries += 1

        async with page2:

            Agodahotel_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/90.0.4430.212 Safari/537.36",
                "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8,zh-CN;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
            }

            await page2.set_extra_http_headers(Agodahotel_headers)
            await page2.goto(page2.url)

            retries = 0
            while True:
                try:

                    # 等待元素加载完成
                    await page2.wait_for_selector("//*[@id='roomGrid']", timeout=20000)

                    html = await page2.content()

                    # 使用异步文件写入数据
                    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                        await f.write(html)

                    logging.info(f"{task_name} - {filename}: 爬取成功")

                    # 随机等待一段时间
                    await random_wait()

                    await page2.close()
                    break

                except Exception as e:
                    logging.error(f"Error: {e}")
                    logging.info(f"{task_name} - {filename}酒店页第 {retries + 1} 次等待元素超时！尝试重新加载")
                    if retries == max_retries:
                        logging.warning(f"{task_name} - {filename}酒店页达到最大重试次数,爬取失败")
                        return  # 达到最大重试次数，退出程序
                    else:
                        # 刷新页面，并递增计数器
                        await page2.reload()
                        retries += 1


async def main():
    # 打开存储 URL 的文件
    with open("urls.txt", "r") as f:
        urls = f.read().splitlines()

    async with async_playwright() as p:

        headless = int(input("任务是否在后台运行："))  # 请求用户输入并将其转换为整数
        if headless == 1:
            headless = True
        else:
            headless = False

        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()

        # 设置页面默认超时时间为60秒
        timeout = 180 * 1000  # 90 minutes in milliseconds
        context.set_default_timeout(timeout)

        tasks = []

        MAX_CONCURRENT_TASKS = int(input("请设置最大运行任务数："))  # 请求用户输入并将其转换为整数 # 控制同时执行的任务数量
        current_task_count = 0  # 当前正在执行的任务数

        max_retries = int(input("请设置最大重试次数："))  # 请求用户输入并将其转换为整数 # 控制最大重试次数

        for i in range(len(urls)):
            if current_task_count >= MAX_CONCURRENT_TASKS:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for completed_task in done:
                    try:
                        await completed_task
                        tasks.remove(completed_task)
                        current_task_count -= 1
                    except Exception as e:
                        logging.error(f"Error while running task: {e}")

            page = await context.new_page()
            page.set_default_timeout(timeout)

            task_name = f"Task {i + 1}"

            filename = clean_filename(urls[i])

            task = asyncio.create_task(
                get_data(page, urls[i], filename, max_retries=max_retries,
                         task_name=task_name))  # 传递 filenames 和 task_name 参数

            tasks.append(task)
            current_task_count += 1

        # 使用 asyncio.as_completed() 按完成顺序等待任务的完成
        for completed_task in asyncio.as_completed(tasks):
            try:
                await completed_task
                tasks.remove(completed_task)
                current_task_count -= 1
            except Exception as e:
                logging.error(f"Error while running task: {e}")

        await browser.close()


if __name__ == '__main__':
    try:
        logging.info("程序开始运行")
        asyncio.run(main())

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
