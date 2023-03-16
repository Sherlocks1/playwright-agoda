import datetime

hotel_choice = input("请输入1选择现有酒店，输入0输入自定义酒店ID：")

if hotel_choice == "1":
    hotels = {"曼谷卡塞特纳瓦敏里沃泰尔酒店": "2918402",
              "王子宫殿酒店": "1043047",
              "北京金隅国际会议中心（双井店）": "8910111"} # 这里是示例酒店列表，您需要替换成您实际可选酒店名和对应ID
    print("可选酒店列表：")
    for index, hotel in enumerate(hotels):
        print(f"{index + 1}. {hotel}")
    selected_hotel_index = int(input("请选择对应数字：")) - 1
    selected_hotel_name = list(hotels.keys())[selected_hotel_index]
    hotel_id = hotels[selected_hotel_name]
    print(f"您选择的酒店为：{selected_hotel_name}（ID：{hotel_id}）")
else:
    hotel_id = input("请输入酒店ID：")

base_url = f"https://search.etrip.net/Hotel/Search?hotelId={hotel_id}&checkIn={{check_in_date}}&checkOut={{check_out_date}}&rooms=2&homeSearch=1&userSearch=1"

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
        url = base_url.format(check_in_date=check_in_date_i.strftime("%Y-%m-%d"), check_out_date=check_out_date_i.strftime("%Y-%m-%d"))
        f.write(url + "\n")

print("已生成URL列表并写入urls.txt文件。")

