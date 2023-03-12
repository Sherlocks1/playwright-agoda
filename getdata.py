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


async def get_data(page, url, filenames, max_retries=2):
    await page.route("**/*.png", lambda route: route.abort())
    await page.route("**/*.jpg", lambda route: route.abort())
    await page.route("**/*.jpeg", lambda route: route.abort())
    await page.route("**/*.gif", lambda route: route.abort())

    retries = 0
    while True:
        try:
            await page.goto(url)

            # 等待元素加载完成
            await page.wait_for_selector("//*[@id='roomGrid']", timeout=90000)

            # 获取网页HTML并保存
            html = await page.content()
            filename = clean_filename(url)
            filenames.append(filename)  # 将文件名添加到列表中
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            await page.close()
            break

        except Exception as e:
            print(f"Error: {e}")
            if retries == max_retries:
                print(f"Max retries ({max_retries}) reached.")
                break
            retries += 1
            print(f"Page load timed out, retrying... (attempt {retries} of {max_retries + 1})")
            await page.reload()


async def main():
    # 打开存储 URL 的文件
    with open("urls.txt", "r") as f:
        urls = f.read().splitlines()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 设置页面默认超时时间为60秒
        timeout = 90 * 1000  # 90 minutes in milliseconds
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
