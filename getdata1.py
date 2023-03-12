import asyncio

from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # 设置页面默认超时时间为60秒
    timeout = 30 * 1000  # 90 minutes in milliseconds
    context.set_default_navigation_timeout(timeout)

    page = await context.new_page()  # 新建页面

    page1 = None
    retries = 0
    while True:
        try:

            await page.goto(
                "https://search.etrip.net/Hotel/Search?hotelId=4387380&checkIn=2023-03-12&checkOut=2023-03-13&rooms=2"
                "&homeSearch=1&userSearch=1")

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
            if retries == 2:
                return  # 达到最大重试次数，退出程序
            else:
                # 刷新页面，并递增计数器
                await page.reload()
                retries += 1

    await page1.goto(page1.url)

    page2 = None
    retries = 0
    while True:
        try:
            async with page1.expect_popup() as page2_info:

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
            if retries == 2:
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
            print(html)

            await page2.close()
            break

        except Exception as e:
            print(f"Error: {e}")
            if retries == 2:
                print(f"酒店页面第 {retries + 1} 次等待元素超时！尝试重新加载")
                if retries == 2:
                    return  # 达到最大重试次数，退出程序
                else:
                    # 刷新页面，并递增计数器
                    await page2.reload()
                    retries += 1

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
