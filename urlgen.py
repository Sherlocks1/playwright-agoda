import datetime

hotel_id = input("请输入酒店ID：")
base_url = f"https://search.etrip.net/Hotel/Search?hotelId={hotel_id}&checkIn={{check_in_date}}&checkOut={{check_out_date}}&rooms=2&homeSearch=1&userSearch=1"

check_in_date_str = input("请输入入住日期（格式为YYYY-MM-DD）：")
check_out_date_str = input("请输入离店日期（格式为YYYY-MM-DD）：")

check_in_date = datetime.datetime.strptime(check_in_date_str, "%Y-%m-%d")
check_out_date = datetime.datetime.strptime(check_out_date_str, "%Y-%m-%d")

num_days = (check_out_date - check_in_date).days

with open("urls.txt", "w") as f:
    for i in range(num_days):
        check_in_date_i = check_in_date + datetime.timedelta(days=i)
        check_out_date_i = check_in_date_i + datetime.timedelta(days=1)
        url = base_url.format(check_in_date=check_in_date_i.strftime("%Y-%m-%d"), check_out_date=check_out_date_i.strftime("%Y-%m-%d"))
        f.write(url + "\n")

print("已生成URL列表并写入urls.txt文件。")

