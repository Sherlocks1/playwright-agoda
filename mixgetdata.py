import os

from playwright.async_api import async_playwright
import asyncio
import re


def clean_filename(url: str) -> str:
    match = re.search(r'checkIn=(\d{4}-\d{2}-\d{1,2})', url)
    if match:
        filename = match.group(1) + ".html"
    else:
        filename = "unknown.html"
    return filename


async def get_data(page, url, filenames, max_retries=4):
    page1 = None
    retries = 0

    while True:
        try:

            await page.goto(url)

            page.set_default_timeout(10000)

            # 等待 AGD-logo 出现
            agd_logo = await page.wait_for_selector("div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']",
                                                    timeout=10000)

            # 单击 AGD-logo
            await agd_logo.click()

            # 等待新窗口打开
            async with page.expect_popup() as page1_info:
                page1 = await page1_info.value
                await page.close()
                break
        except Exception as e:
            print(f"Error: {e}")
            print(f"etrip第 {retries + 1} 次等待元素超时！尝试重新加载")
            if retries == 4:
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    await page1.goto(page1.url)

    page2 = None
    retries = 0
    async with page1.expect_popup() as page2_info:
        while True:
            try:

                # 等待链接出现
                link = await page1.wait_for_selector(
                    'xpath=/html[1]/body[1]/div[11]/div[1]/div[3]/div[1]/div[1]/div[2]/div[1]/div[3]/ol[1]/li[1]/div['
                    '2]/a[1]/div[1]/div[3]/div[1]',
                    timeout=10000)

                # 单击链接
                await link.click()

                page2 = await page2_info.value
                await page1.close()
                break
            except Exception as e:
                print(f"Error: {e}")
                print(f"agoda列表页第 {retries + 1} 次等待元素超时！尝试重新加载")
                if retries == 4:
                    return  # 达到最大重试次数，退出程序
                else:
                    # 刷新页面，并递增计数器
                    await page1.reload()
                    retries += 1

    await page2.goto(page2.url)

    retries = 0
    while True:
        try:

            # 等待元素加载完成
            await page2.wait_for_selector("//*[@id='roomGrid']", timeout=10000)

            html = await page2.content()
            filename = clean_filename(url)
            filenames.append(filename)  # 将文件名添加到列表中
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            print(filenames)

            await page2.close()
            break

        except Exception as e:
            print(f"Error: {e}")
            if retries == 4:
                print(f"酒店页面第 {retries + 1} 次等待元素超时！尝试重新加载")
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page2.reload()
                retries += 1


async def main():
    # 打开存储 URL 的文件
    with open("urls.txt", "r") as f:
        urls = f.read().splitlines()

    cache_dir = './cache_directory'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    print('Cache directory:', os.path.abspath(cache_dir))

    async with async_playwright() as p:

        print('Launching browser')
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 设置页面默认超时时间为60秒
        timeout = 180 * 1000  # 90 minutes in milliseconds
        context.set_default_navigation_timeout(timeout)

        tasks = []
        filenames = []

        # 控制同时执行的任务数量
        MAX_CONCURRENT_TASKS = 3
        current_task_count = 0
        total_task_count = len(urls)

        for i in range(len(urls)):
            page = await context.new_page()
            task = asyncio.create_task(get_data(page, urls[i], filenames))  # 传递 filenames 参数
            tasks.append(task)

            # 等待当前任务数量小于最大限制
            while current_task_count >= MAX_CONCURRENT_TASKS:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                current_task_count -= len(done)

            current_task_count += 1

        # 等待所有任务完成
        while tasks:
            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            current_task_count -= len(done)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
