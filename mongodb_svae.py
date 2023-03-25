import pymongo
from datetime import datetime

# 数据库连接信息
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel'] # 数据库名称
collection = db['booking'] # 集合名称

# 待插入数据
data = [{'hotel_name': '曼谷卡塞特纳瓦敏里沃泰尔酒店 (Livotel Hotel Kaset Nawamin Bangkok)', 'check_in': '2023年3月26日', 'room_name': '标准房(双床) (Standard Twin Room)', 'room_price': 141, 'room_status': '**空房有限**'}, {'hotel_name': '曼谷卡塞特纳瓦敏里沃泰尔酒店 (Livotel Hotel Kaset Nawamin Bangkok)', 'check_in': '2023年3月26日', 'room_name': '标准房(双人床) (Standard Double Room)', 'room_price': 141, 'room_status': '**空房有限**'}, {'hotel_name': '曼谷卡塞特纳瓦敏里沃泰尔酒店 (Livotel Hotel Kaset Nawamin Bangkok)', 'check_in': '2023年3月26日', 'room_name': '家庭房 (Family Room)', 'room_price': None, 'room_status': '已订完'}, {'hotel_name': '曼谷卡塞特纳瓦敏里沃泰尔酒店 (Livotel Hotel Kaset Nawamin Bangkok)', 'check_in': '2023年3月26日', 'room_name': '豪华双人房 (Deluxe Double Room)', 'room_price': 183, 'room_status': '我们仅剩最后2间房'}, {'hotel_name': '曼谷卡塞特纳瓦敏里沃泰尔酒店 (Livotel Hotel Kaset Nawamin Bangkok)', 'check_in': '2023年3月26日', 'room_name': '套房 (Suite)', 'room_price': 238, 'room_status': '我们仅剩最后4间房'}]

# 对数据进行转换和格式化
for doc in data:
    # 将日期字符串转换为 datetime 对象
    iso_date = datetime.strptime(doc['check_in'], '%Y年%m月%d日')
    # 更新 doc 中的 check_in 字段值
    doc['check_in'] = iso_date

    # 对价格进行格式化
    if doc['room_price'] is not None:
        doc['room_price'] = int(doc['room_price'])

# 将数据插入到 MongoDB 集合中
result = collection.insert_many(data)
print(result.inserted_ids)
# 输出插入后的文档 ID 列表
