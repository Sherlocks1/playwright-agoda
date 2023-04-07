# -*- coding = utf-8 -*-
# @Time : 2023/4/7 11:08
# @Author : Sherlock
# @File : text1.py
# @Software : PyCharm
import datetime
from crawler import crawler
import asyncio

def hotel_info():
    hotels = {
        "曼谷卡塞特纳瓦敏里沃泰尔酒店": "2918402",
        "王子宫殿酒店": "1043047",
        "艾里四分之一UHG酒店": "4387380",
        "江陵Hi Ocean镜浦酒店": "5272524",
        "镜浦天空酒店": "3579492",
        "芽庄皇宫酒店": "5010957",
        "芽庄槟榔酒店": "4817166",
        "长滩岛航路与蓝海度假村": "1599297",
    }
    hotel_choice = input("请输入1选择现有酒店，输入0输入自定义酒店ID：")
    if hotel_choice == "1":
        print("可选酒店列表：")
        for index, hotel in enumerate(hotels):
            print(f"{index + 1}. {hotel}")
        hotel_index = int(input("请选择对应数字：")) - 1
        hotel_name = list(hotels.keys())[hotel_index]
        hotel_id = hotels[hotel_name]
        print(f"您选择的酒店为：{hotel_name}（ID：{hotel_id}）")
        return hotel_name, hotel_id
    else:
        hotel_name = input("请输入酒店名称：")
        hotel_id = input("请输入酒店ID：")
        return hotel_name, hotel_id


def urlgen(hotel_name, hotel_id):
    base_url = f"https://search.etrip.net/Hotel/Search?hotelId={hotel_id}&checkIn={{check_in_date}}&checkOut={{check_out_date}}&rooms=2&userSearch=1"
    check_in_date_str = input("请输入入住日期（格式为MM-DD）：")
    check_out_date_str = input("请输入离店日期（格式为MM-DD）：")

    # 将年份设置为当前年份
    current_year = datetime.datetime.now().year
    check_in_date_str_with_year = f"{current_year}-{check_in_date_str}"
    check_out_date_str_with_year = f"{current_year}-{check_out_date_str}"

    check_in_date = datetime.datetime.strptime(check_in_date_str_with_year, "%Y-%m-%d")
    check_out_date = datetime.datetime.strptime(check_out_date_str_with_year, "%Y-%m-%d")

    num_days = (check_out_date - check_in_date).days

    with open("urls.txt", "w") as f:
        for i in range(num_days):
            check_in_date_i = check_in_date + datetime.timedelta(days=i)
            check_out_date_i = check_in_date_i + datetime.timedelta(days=1)
            url = base_url.format(
                check_in_date=check_in_date_i.strftime("%Y-%m-%d"),
                check_out_date=check_out_date_i.strftime("%Y-%m-%d")
            )
            f.write(url + "\n")

    print("已生成URL列表并写入urls.txt文件。")


async def main():
    hotel_name, hotel_id = hotel_info()
    urlgen(hotel_name, hotel_id)
    with open("urls.txt", "r") as f:
        urls = f.readlines()
    tasks = []
    for url in urls:
        task = asyncio.create_task(crawler(hotel_name, url.strip()))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)


# 主程序入口
if __name__ == "__main__":
    asyncio.run(main())