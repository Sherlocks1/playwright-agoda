# -*- coding = utf-8 -*-
# @Time : 2023/3/30 22:56
# @Author : Sherlock
# @File : explain_data.py
# @Software : PyCharm
from bs4 import BeautifulSoup
import re
from datetime import datetime

find_room_name = re.compile(r'<span class="MasterRoom__HotelName" data-selenium="masterroom-title-name">(.*?)</span>')
find_room_price = re.compile(r'<strong data-ppapi="(.*?)/strong>')
find_room_status = re.compile(r'<strong class=".*font-size-12">(.*?)</strong>')
find_soldoutroom_name = re.compile(r'<h5\s+class="[^"]*Headingstyled[^"]*">(.*?)<\/h5>')


def explain_data(html):
    soup = BeautifulSoup(html, "html.parser")
    hotel_name = soup.select_one('p.HeaderCerebrum__AdaName').text
    check_in = soup.select_one('#check-in-box > div > div > div > div:nth-child(1)').get_text(strip=True)
    rooms = soup.select('div.MasterRoom, div.Box-sc-kv6pi1-0.iClxWR')
    data = []
    parse_time = datetime.utcnow()  # 获取当前时间

    for eachroom in rooms:
        if 'MasterRoom' in eachroom['class']:
            # 解析规则 1
            room_name = re.findall(find_room_name, str(eachroom))
            room_price_match = re.search(find_room_price, str(eachroom))
            room_price_str = room_price_match.group(1) if room_price_match else ""
            room_price_cleaned = "".join(c for c in room_price_str if c.isdigit())
            room_price = int(room_price_cleaned) if room_price_cleaned else None
            room_status_match = re.findall(find_room_status, str(eachroom))
            room_status = room_status_match[0] if room_status_match else None
            data.append({
                'hotel_name': hotel_name,
                'check_in': check_in,
                'room_name': room_name[0] if room_name else None,
                'room_price': room_price,
                'room_status': room_status,
                'parse_time': parse_time  # 添加解析时间
            })
        elif 'Box-sc-kv6pi1-0' in eachroom['class']:
            # 解析规则 2
            room_name = re.findall(find_soldoutroom_name, str(eachroom))
            room_price = None
            room_status = "已订完"
            data.append({
                'hotel_name': hotel_name,
                'check_in': check_in,
                'room_name': room_name[0] if room_name else None,
                'room_price': room_price,
                'room_status': room_status,
                'parse_time': parse_time  # 添加解析时间
            })
    return data