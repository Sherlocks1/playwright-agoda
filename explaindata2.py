from bs4 import BeautifulSoup
import re

find_room_name = re.compile(r'<span class="MasterRoom__HotelName" data-selenium="masterroom-title-name">(.*?)</span>')
find_room_price = re.compile(r'<strong data-ppapi="(.*?)/strong>')
find_room_status = re.compile(r'<strong class=".*font-size-12">(.*?)</strong>')
find_soldoutroom_name = re.compile(r'<h5\s+class="[^"]*Headingstyled[^"]*">(.*?)<\/h5>')

def explain_data(html):
    soup = BeautifulSoup(html, "html.parser")
    check_in = soup.select_one('#check-in-box > div > div > div > div:nth-child(1)').get_text(strip=True)
    rooms = soup.select('div.MasterRoom, div.Box-sc-kv6pi1-0.iClxWR')
    data = []
    for eachroom in rooms:
        if 'MasterRoom' in eachroom['class']:
            # 解析规则 1
            room_name = re.findall(find_room_name, str(eachroom))
            room_price_match = re.findall(find_room_price, str(eachroom))
            room_price = room_price_match[0] if room_price_match else "无价格"
            room_status_match = re.findall(find_room_status, str(eachroom))
            room_status = room_status_match[0] if room_status_match else "无状态"
            data.append([check_in, room_name, room_price, room_status])
        elif 'Box-sc-kv6pi1-0' in eachroom['class']:
            # 解析规则 2
            room_name = re.findall(find_soldoutroom_name, str(eachroom))
            room_price = "已订完"
            room_status = "已订完"
            data.append([check_in, room_name, room_price, room_status])

    return data

