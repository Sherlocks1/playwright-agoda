# -*- coding = utf-8 -*-
# @Time : 2023/4/3 0:13
# @Author : Sherlock
# @File : get_data.py
# @Software : PyCharm
import asyncio
import logging

from tools import random_wait
from explain_data import explain_data
from save_data import save_data


async def get_data(page, url, date, max_retries, task_number=None, headers=None, hotel_name=None):
    logging.info(f"{hotel_name} - {task_number} - {date}: 任务开始")

    retries = 0

    while True:
        try:
            await page.set_extra_http_headers(headers)
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

        except Exception as error:

            logging.error(f"{hotel_name} - {task_number} - {date}: Error - {error}")
            logging.info(f"{hotel_name} - {task_number} - {date}: Etrip页第 {retries + 1} 次等待元素超时！尝试重新加载")
            if retries == max_retries:
                logging.warning(f"{hotel_name} - {task_number} - {date}: Etrip页达到最大重试次数,爬取失败")
                await page.close()
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    async with page1:

        await page1.set_extra_http_headers(headers)

        # page1.on("response", lambda response: (
        #     print({hotel_name}, {task_number}, {date}, "page1响应状态 <<", response.status, response.url, response.ok)))

        def response_handler(response):
            if response.status == 404:
                # 进行重新开始操作
                logging.warning(f"{hotel_name} - {task_number} - {date}: Agoda列表页响应状态为404，尝试重新开始")
                # asyncio.ensure_future(get_data(page, url, date, max_retries, task_number, headers, hotel_name))
                # return

        page1.on("response", response_handler)

        page1.on('close', lambda: print(f'{hotel_name} - {task_number} - {date}: page1已关闭'))

        await page1.goto(page1.url)
        logging.info(f"{hotel_name} - {task_number} - {date}: Agoda列表页 - 成功跳转")
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
                except Exception as error:
                    logging.error(f"{hotel_name} - {task_number} - {date}: Error - {error}")
                    logging.info(
                        f"{hotel_name} - {task_number} - {date}Agoda列表页第 {retries + 1} 次等待元素超时！尝试重新加载")
                    if retries == max_retries:
                        logging.warning(f"{hotel_name} - {task_number} - {date}: Agoda列表页达到最大重试次数,爬取失败")
                        await page1.close()
                        return  # 达到最大重试次数，退出程序
                    else:
                        # 刷新页面，并递增计数器
                        await page1.reload()
                        retries += 1

        async with page2:

            await page2.set_extra_http_headers(headers)
            # page2.on("response", lambda response: (
            #     print({hotel_name}, {task_number}, {date}, "page2响应状态 <<", response.status, response.url,
            #           response.ok)))

            await page2.goto(page2.url)

            logging.info(f"{hotel_name} - {task_number} - {date}: 酒店页 - 成功跳转")

            retries = 0
            while True:
                try:

                    # 等待元素加载完成
                    await page2.wait_for_selector("//*[@id='roomGrid']", timeout=20000)

                    html = await page2.content()

                    data = explain_data(html)

                    save_data(data)

                    logging.info(f"{hotel_name} - {task_number} - {date}: 爬取成功")

                    # 随机等待一段时间
                    await random_wait()

                    await page2.close()

                    break

                except Exception as error:
                    logging.error(f"Error: {error}")
                    logging.info(
                        f"{hotel_name} - {task_number} - {date}酒店页第 {retries + 1} 次等待元素超时！尝试重新加载")
                    if retries == max_retries:
                        logging.warning(f"{hotel_name} - {task_number} - {date}酒店页达到最大重试次数,爬取失败")

                    else:
                        # 刷新页面，并递增计数器
                        await page2.reload()
                        retries += 1
