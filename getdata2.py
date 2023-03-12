import asyncio
from playwright.async_api import Playwright, async_playwright


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # 设置页面默认超时时间为30秒
    timeout = 30 * 1000
    context.set_default_navigation_timeout(timeout)

    page1 = None
    retries = 0
    while True:
        try:
            page = await context.new_page()
            await page.goto(
                "https://search.etrip.net/Hotel/Search?hotelId=4387380&checkIn=2023-03-12&checkOut=2023-03-13&rooms=2&homeSearch=1&userSearch=1")

            # 点击AGD-logo
            await page.locator("div[class='css-170e3kd e19j9nj21'] img[alt='AGD-logo']").click()

            # 等待新窗口打开
            async with page.expect_popup() as page1_info:
                page1 = await page1_info.value
                break
        except Exception as e:
            print(f"Error: {e}")
            print(f"etrip第 {retries + 1} 次等待元素超时！")
            if retries == 2:
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    # 导航到新窗口的URL地址
    await page1.goto(page1.url)

    retries = 0
    while True:
        try:
            # 等待链接出现
            await page1.wait_for_selector("a[href*='quarter-ari-uhg-shanghai-plus']", state="visible", timeout=60000)

            # 单击链接
            await page1.get_by_role("link",
                                    name="UHG The Quarter阿里酒店【SHA Plus+】 (The Quarter Ari by UHG (SHA Plus+))",
                                    exact=True).click()

            # 等待元素加载完成
            await page1.wait_for_selector("//*[@id='roomGrid']")
            break
        except TimeoutError:
            print(f"第 {i + 1} 次等待元素超时！")
            if i == 1:
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面
                await page1.reload()

    html = await page1.content()
    print(html)

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
