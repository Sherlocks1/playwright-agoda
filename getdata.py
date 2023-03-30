import asyncio
import logging
import re

import pymongo
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime
from tools import clean_filename
from tools import random_wait

find_room_name = re.compile(r'<span class="MasterRoom__HotelName" data-selenium="masterroom-title-name">(.*?)</span>')
find_room_price = re.compile(r'<strong data-ppapi="(.*?)/strong>')
find_room_status = re.compile(r'<strong class=".*font-size-12">(.*?)</strong>')
find_soldoutroom_name = re.compile(r'<h5\s+class="[^"]*Headingstyled[^"]*">(.*?)<\/h5>')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("my_log_file.log"),
        logging.StreamHandler(),
    ],
)


def explain_data(html):
    soup = BeautifulSoup(html, "html.parser")
    hotel_name = soup.select_one('p.HeaderCerebrum__AdaName').text
    check_in = soup.select_one('#check-in-box > div > div > div > div:nth-child(1)').get_text(strip=True)
    rooms = soup.select('div.MasterRoom, div.Box-sc-kv6pi1-0.iClxWR')
    data = []
    parse_time = datetime.utcnow()  # 获取当前时间
    for eachroom in rooms:
        if 'MasterRoom' in eachroom['class']:
            # 解析规则 1
            room_name = re.findall(find_room_name, str(eachroom))
            room_price_match = re.search(find_room_price, str(eachroom))
            room_price_str = room_price_match.group(1) if room_price_match else ""
            room_price_cleaned = "".join(c for c in room_price_str if c.isdigit())
            room_price = int(room_price_cleaned) if room_price_cleaned else None
            room_status_match = re.findall(find_room_status, str(eachroom))
            room_status = room_status_match[0] if room_status_match else None
            data.append({
                'hotel_name': hotel_name,
                'check_in': check_in,
                'room_name': room_name[0] if room_name else None,
                'room_price': room_price,
                'room_status': room_status,
                'parse_time': parse_time  # 添加解析时间
            })
        elif 'Box-sc-kv6pi1-0' in eachroom['class']:
            # 解析规则 2
            room_name = re.findall(find_soldoutroom_name, str(eachroom))
            room_price = None
            room_status = "已订完"
            data.append({
                'hotel_name': hotel_name,
                'check_in': check_in,
                'room_name': room_name[0] if room_name else None,
                'room_price': room_price,
                'room_status': room_status,
                'parse_time': parse_time  # 添加解析时间
            })
    return data


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
            }

            await page2.set_extra_http_headers(Agodahotel_headers)
            await page2.goto(page2.url)

            retries = 0
            while True:
                try:

                    # 等待元素加载完成
                    await page2.wait_for_selector("//*[@id='roomGrid']", timeout=20000)

                    html = await page2.content()

                    data = explain_data(html)

                    # 连接 MongoDB 数据库
                    client = pymongo.MongoClient('mongodb://localhost:27017/')
                    db = client['hotel']
                    collection = db['booking']

                    # 对数据进行转换和格式化
                    for doc in data:
                        # 将日期字符串转换为 datetime 对象
                        iso_date = datetime.strptime(doc['check_in'], '%Y年%m月%d日')
                        # 更新 doc 中的 check_in 字段值
                        doc['check_in'] = iso_date

                        # 对价格进行格式化
                        if doc['room_price'] is not None:
                            doc['room_price'] = int(doc['room_price'])

                        # 根据酒店名称、入住日期和房型进行匹配
                        query = {"hotel_name": doc["hotel_name"],
                                 "check_in": doc["check_in"],
                                 "room_name": doc["room_name"]}

                        # 查找已有文档
                        existing_doc = collection.find_one(query)

                        if existing_doc is None:
                            # 如果没有匹配到文档，则插入一条新的文档
                            result = collection.insert_one(doc)
                            print('新增:', result.inserted_id)
                        else:
                            # 如果已经匹配到文档，则进行更新操作
                            new_price = doc['room_price']
                            new_status = doc['room_status']

                            room_price_is_modified = False
                            room_status_is_modified = False

                            if existing_doc['room_price'] != new_price:
                                # 价格发生变化，更新数据，并标记为已修改
                                doc['room_price_is_modified'] = True
                                room_price_is_modified = True

                            if existing_doc['room_status'] != new_status:
                                # 房态发生变化，更新数据，并标记为已修改
                                doc['room_status_is_modified'] = True
                                room_status_is_modified = True

                            if not room_price_is_modified and not room_status_is_modified:
                                # 如果价格和房态没有变化，则将相应的标志设置为 False
                                doc['room_price_is_modified'] = False
                                doc['room_status_is_modified'] = False
                                doc['parse_time'] = datetime.now()  # 更新解析时间
                                print('无变化')
                            else:
                                # 如果价格或房态发生了变化，则将这些变化信息输出到控制台，并更新 MongoDB 中的文档，同时标记相关字段为已修改
                                update_result = collection.update_one(query, {"$set": doc})
                                if update_result.modified_count == 1:
                                    print(f'更新: {existing_doc["_id"]}')
                                    doc['_id'] = existing_doc['_id']
                                else:
                                    print('更新失败')

                                if room_price_is_modified:
                                    print(
                                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间价格从{existing_doc['room_price']}元变为{new_price}元")
                                if room_status_is_modified:
                                    print(
                                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间房态从{existing_doc['room_status']}变为{new_status}")

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


async def crawler():
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
