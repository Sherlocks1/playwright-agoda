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
            result = collection.insert_one(doc)
            print('新增:', result.inserted_id)
        else:
            # 如果已经匹配到文档，则进行更新操作
            new_price = doc['room_price']
            new_status = doc['room_status']

            room_price_is_modified = False
            room_status_is_modified = False

            if existing_doc['room_price'] != new_price:
                # 价格发生变化，更新数据，并标记为已修改
                doc['room_price_is_modified'] = True
                room_price_is_modified = True

            if existing_doc['room_status'] != new_status:
                # 房态发生变化，更新数据，并标记为已修改
                doc['room_status_is_modified'] = True
                room_status_is_modified = True

            if not room_price_is_modified and not room_status_is_modified:
                # 如果价格和房态没有变化，则将相应的标志设置为 False
                doc['room_price_is_modified'] = False
                doc['room_status_is_modified'] = False
                doc['parse_time'] = datetime.now()  # 更新解析时间
                print('无变化')
            else:
                # 如果价格或房态发生了变化，则将这些变化信息输出到控制台，并更新 MongoDB 中的文档，同时标记相关字段为已修改
                update_result = collection.update_one(query, {"$set": doc})
                if update_result.modified_count == 1:
                    print(f'更新: {existing_doc["_id"]}')
                    doc['_id'] = existing_doc['_id']
                else:
                    print('更新失败')

                if room_price_is_modified:
                    print(
                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间价格从{existing_doc['room_price']}元变为{new_price}元")
                if room_status_is_modified:
                    print(
                        f"{existing_doc['hotel_name']}-{existing_doc['check_in'].strftime('%Y年%m月%d日')}-{existing_doc['room_name']}房间房态从{existing_doc['room_status']}变为{new_status}")
