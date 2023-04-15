# -*- coding = utf-8 -*-
# @Time : 2023/3/30 22:49
# @Author : Sherlock
# @File : save_data.py
# @Software : PyCharm

import pymongo
from datetime import datetime


def save_data(data):
    # 连接 MongoDB 数据库
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['hotel']
    collection = db['booking']

    # 获取当前日期
    today = datetime.today().date().strftime("%Y-%m-%d")
    today_datetime = datetime.strptime(today, "%Y-%m-%d")

    # 清除过期数据
    result = collection.delete_many({"check_in": {"$lt": today_datetime}})
    # result = collection.delete_many({})
    # print(f"已清除 {result.deleted_count} 条过期数据")

    # 对数据进行转换和格式化
    for doc in data:
        # 将日期字符串转换为 datetime 对象
        iso_date = datetime.strptime(doc['check_in'], '%Y年%m月%d日')
        # 更新 doc 中的 check_in 字段值
        doc['check_in'] = iso_date

        # 对价格进行格式化
        if doc['room_price'] is not None:
            doc['room_price'] = int(doc['room_price'])

        # 根据酒店名称、入住日期和房型进行匹配
        query = {"hotel_name": doc["hotel_name"],
                 "check_in": doc["check_in"],
                 "room_name": doc["room_name"]}

        # 查找已有文档
        existing_doc = collection.find_one(query)

        if existing_doc is None:
            # 如果没有匹配到文档，则插入一条新的文档
            if doc['check_in'] >= today_datetime:
                doc['room_price_change'] = '新增'
                doc['room_status_change'] = '新增'
                result = collection.insert_one(doc)
                print('新增:', result.inserted_id)
            else:
                print(f"该条数据的 check_in 日期早于当前日期，不进行插入操作: {doc}")
        else:
            # 如果已经匹配到文档，则进行更新操作
            new_price = doc['room_price']
            new_status = doc['room_status']

            room_price_change = None
            room_status_change = None

            if existing_doc['room_price'] != new_price:
                # 价格发生变化，更新数据，并标记为已修改
                room_price_change = str(existing_doc['room_price']) + ' --> ' + str(new_price)

            if existing_doc['room_status'] != new_status:
                # 房态发生变化，更新数据，并标记为已修改
                room_status_change = existing_doc['room_status'] + ' --> ' + new_status

            if room_price_change is None and room_status_change is None:
                # 如果价格和房态都没有变化，打印 "无变化"
                doc['parse_time'] = datetime.now()
                doc['room_price_change'] = '无变化'
                doc['room_status_change'] = '无变化'
                collection.update_one(query, {"$set": doc})
                print('无变化')
            else:
                if room_price_change is None:
                    doc['room_price_change'] = '无变化'
                if room_price_change is not None:
                    doc['room_price_change'] = room_price_change

                if room_status_change is None:
                    doc['room_status_change'] = '无变化'
                if room_status_change is not None:
                    doc['room_status_change'] = room_status_change

                doc['parse_time'] = datetime.now()  # 更新解析时间

                update_result = collection.update_one(query, {"$set": doc})
                if update_result.modified_count == 1:
                    print(f'更新: {existing_doc["_id"]}')
                    doc['_id'] = existing_doc['_id']
                else:
                    print('更新失败')

                if room_price_change is not None:
                    print(
                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间价格从{existing_doc['room_price']}元变为{new_price}元")

                if room_status_change is not None:
                    print(
                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间房态从{existing_doc['room_status']}变为{new_status}")

