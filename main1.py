# -*- coding = utf-8 -*-
# @Time : 2023/4/7 11:08
# @Author : Sherlock
# @File : main1.py
# @Software : PyCharm
import datetime
from crawler import crawler
import asyncio


def hotel_info():
    hotels = {
        "曼谷卡塞特纳瓦敏里沃泰尔酒店": {"id": "2918402", "selected": False, "num_days": None},
        "王子宫殿酒店": {"id": "1043047", "selected": False, "num_days": None},
        "艾里四分之一UHG酒店": {"id": "4387380", "selected": False, "num_days": None},
        "江陵Hi Ocean镜浦酒店": {"id": "5272524", "selected": False, "num_days": None},
        "镜浦天空酒店": {"id": "3579492", "selected": False, "num_days": None},
        "芽庄皇宫酒店": {"id": "5010957", "selected": False, "num_days": None},
        "芽庄槟榔酒店": {"id": "4817166", "selected": False, "num_days": None},
        "长滩岛航路与蓝海度假村": {"id": "1599297", "selected": False, "num_days": None},
    }
    selected_hotels = []
    while True:
        print("可选酒店列表：")
        for index, hotel in enumerate(hotels):
            status = "[已选]" if hotels[hotel]["selected"] else ""
            print(f"{index + 1}. {hotel} {status}")
        print(f"0. 确认选择（已选{len(selected_hotels)}家酒店）")
        choice = input("请选择对应数字：")
        if choice == "0":
            if len(selected_hotels) == 0:
                print("至少选择一家酒店！")
                continue
            else:
                break
        try:
            hotel_index = int(choice) - 1
            hotel_name = list(hotels.keys())[hotel_index]
            hotel_id = hotels[hotel_name]["id"]
            if hotels[hotel_name]["selected"]:
                print("该酒店已被选中，请重新选择！")
            else:
                num_days = input("请输入需要爬取的天数：")
                hotels[hotel_name]["selected"] = True
                hotels[hotel_name]["num_days"] = int(num_days)
                selected_hotels.append({"name": hotel_name, "id": hotel_id, "num_days": num_days})
        except (ValueError, IndexError):
            print("无效的输入，请重新选择！")
    print("您已选中以下酒店：")
    for hotel in selected_hotels:
        print(f"{hotel['name']}（ID：{hotel['id']}，爬取天数：{hotels[hotel['name']]['num_days']}）")
        urlgen(hotel["name"], hotel["id"], hotels[hotel["name"]]["num_days"])
    return selected_hotels


def urlgen(hotel_name, hotel_id, num_days):
    base_url = f"https://search.etrip.net/Hotel/Search?hotelId={hotel_id}&checkIn={{check_in_date}}&checkOut={{check_out_date}}&rooms=2&userSearch=1"

    # 将年份设置为当前年份
    current_year = datetime.datetime.now().year

    check_in_date = datetime.datetime.today()
    check_out_date = check_in_date + datetime.timedelta(days=num_days)

    with open(f"{hotel_name}_urls.txt", "w") as f:
        for i in range(num_days):
            check_in_date_i = check_in_date + datetime.timedelta(days=i)
            check_out_date_i = check_in_date + datetime.timedelta(days=i + 1)  # 修改这行代码
            url = base_url.format(
                check_in_date=check_in_date_i.strftime("%Y-%m-%d"),
                check_out_date=check_out_date_i.strftime("%Y-%m-%d")
            )
            f.write(url + "\n")

    print(f"已生成{hotel_name}的URL列表并写入{hotel_name}_urls.txt文件。")


async def main():
    hotels = hotel_info()
    limit = asyncio.Semaphore(1)  # 限制同时运行的任务数量为1
    results = []
    for hotel in hotels:
        hotel_name = hotel["name"]
        async with limit:
            result = await crawler(hotel_name)
            results.append(result)
    for result in results:
        print(result)


# 主程序入口
if __name__ == "__main__":
    asyncio.run(main())
