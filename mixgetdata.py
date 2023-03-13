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

            await page.goto(url, timeout=60000)

            await page.wait_for_selector("div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']", timeout=90000)

            # 点击AGD-logo
            await page.locator("div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']").click()

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

                # 单击链接
                await page1.get_by_role("link",
                                        name="UHG The Quarter阿里酒店【SHA Plus+】 (The Quarter Ari by UHG (SHA Plus+))",
                                        exact=True).click()
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
            await page2.wait_for_selector("//*[@id='roomGrid']", timeout=90000)

            html = await page2.content()
            filename = clean_filename(url)
            filenames.append(filename)  # 将文件名添加到列表中
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

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

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 设置页面默认超时时间为60秒
        timeout = 5 * 1000  # 90 minutes in milliseconds
        context.set_default_navigation_timeout(timeout)

        tasks = []
        filenames = []
        for i in range(len(urls)):
            page = await context.new_page()
            tasks.append(asyncio.create_task(get_data(page, urls[i], filenames)))  # 传递 filenames 参数
        await asyncio.gather(*tasks)

        print(filenames)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
