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
    }  # 这里是示例酒店列表，您需要替换成您实际可选酒店名和对应ID

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

