from bs4 import BeautifulSoup

def explain_data(html):
    soup = BeautifulSoup(html, 'html5lib')

    check_in = soup.select_one('#check-in-box > div > div > div > div:nth-child(1)').get_text(strip=True)
    rooms = soup.select('div.MasterRoom, div.Box-sc-kv6pi1-0.iClxWR')
    data = []
    for eachroom in rooms:
        if 'MasterRoom' in eachroom['class']:
            # 解析规则 1
            room_name = eachroom.select_one('.MasterRoom__HotelName').text.strip()
            room_price_match = eachroom.select_one('div.CrossedOutPrice[data-element-value]')
            room_price = room_price_match['data-element-value'] if room_price_match else "无价格"
            room_status_match = eachroom.select_one('strong.font-size-12')
            room_status = room_status_match.text.strip() if room_status_match else "无状态"
            data.append([check_in, room_name, room_price, room_status])
        elif 'Box-sc-kv6pi1-0' in eachroom['class']:
            # 解析规则 2
            room_name = eachroom.select_one('.Headingstyled__HeadingStyled-sc-v3bqq6-0').text.strip()
            room_price = "已订完"
            room_status = "已订完"
            data.append([check_in, room_name, room_price, room_status])

    return data


