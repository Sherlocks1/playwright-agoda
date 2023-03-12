from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="state.json")
    page = context.new_page()
    page.set_default_timeout(60000)
    page.goto("https://search.etrip.net/Hotel/Search?hotelId=1756946&checkIn=2023-03-11&checkOut=2023-03-12&rooms=2&userSearch=1")
    with page.expect_popup() as page1_info:
        page.locator("xpath=//html/body/div[1]/section/div/div/main/div[1]/div[1]/div/div/div/div[1]/div/div/div/div/div[3]/a/div/div[2]/div[5]/button").click()
    page1 = page1_info.value
    page1.goto("https://www.agoda.cn/zh-cn/search?NumberofAdults=2&NumberofChildren=0&Rooms=1&checkin=2023-03-11&checkout=2023-03-12&cid=1807747&currency=CNY&mcid=3038&oid=oyB5JiFhiA-8&tag=80a0a556-f72d-4565-984e-4c5bc18261e1&selectedproperty=287432&city=16056&adults=2&children=0&hc=CNY&los=1")
    with page1.expect_popup() as page2_info:
        page1.get_by_role("link", name="卡利马度假村及水疗中心【SHA Extra Plus】 (Kalima Resort & Spa (SHA Extra plus))", exact=True).click()
    page2 = page2_info.value

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)