import asyncio
from playwright.async_api import async_playwright


async def fetch_page(url):
    attempts = 0
    while attempts < 3:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(storage_state="state.json")
                page = await context.new_page()
                await page.goto(url, timeout=60000)
                while True:
                    try:
                        await page.wait_for_selector("//div[@class='css-170e3kd e19j9nj21']//img[@alt='AGD-logo']", timeout=5000)
                        break
                    except:
                        await page.reload()
                content = await page.content()
                await browser.close()
                return content
        except Exception as e:
            print(f"Error: {e}")
            attempts += 1
    return None


async def main():
    url = 'https://search.etrip.net/Hotel/Search?hotelId=1756946&checkIn=2023-03-11&checkOut=2023-03-12&rooms=2&userSearch=1'
    content = await fetch_page(url)
    if content:
        print(content)
    else:
        print("Failed to fetch page")


asyncio.run(main())