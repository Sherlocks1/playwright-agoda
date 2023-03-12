from bs4 import BeautifulSoup
import re

# 编译正则表达式
find_room_name = re.compile(r'<span class="MasterRoom__HotelName" data-selenium="masterroom-title-name">(.*?)</span>')
find_room_price = re.compile(r'<strong data-ppapi="(.*?)/strong>')
find_room_status = re.compile(r'<strong class=".*font-size-12">(.*?)</strong>')
find_soldoutroom_name = re.compile(r'<h5\s+class="[^"]*Headingstyled[^"]*">(.*?)<\/h5>')


def explain_data(html):
    soup = BeautifulSoup(html, "html.parser")
    check_in = soup.select_one('#check-in-box > div > div > div > div:nth-child(1)').get_text(strip=True)

    # 使用更具体的选择器
    rooms = soup.select('div.MasterRoom, div.Box-sc-kv6pi1-0.iClxWR')

    # 使用列表推导式和map函数
    data = [[check_in,
             re.findall(find_room_name, str(eachroom)),
             re.findall(find_room_price, str(eachroom))[0] if re.findall(find_room_price, str(eachroom)) else "无价格",
             re.findall(find_room_status, str(eachroom))[0] if re.findall(find_room_status,
                                                                          str(eachroom)) else "无状态"]
            if 'MasterRoom' in eachroom['class']
            else [check_in,
                  re.findall(find_soldoutroom_name, str(eachroom)),
                  "已订完",
                  "已订完"]
            for eachroom in rooms]

    return data