import sqlite3
import os
from datetime import datetime
from explaindata2 import explain_data
import re

# 定义一个正则表达式模式，用于查找价格
price_pattern = r'[0-9,]+\.*[0-9]*'

# 指定 SQLite 数据库文件的路径为当前工作目录下的 results.db 文件
db_path = "results.db"

# 如果文件已存在，则删除它
if os.path.exists(db_path) and os.path.isfile(db_path):
    os.remove(db_path)

# 创建新的 SQLite 数据库文件
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 创建表格
c.execute('''CREATE TABLE hotel (
                check_in TEXT,
                room_name TEXT,
                price REAL,
                status TEXT);''')

# 初始化数据列表
data = []

for filename in os.listdir("."):
    if filename.endswith(".html"):
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
            parsed_data = explain_data(html_content)

            # 将日期字符串转换为 datetime 对象
            for row in parsed_data:
                date_string = row[0].replace("年", "-").replace("月", "-").replace("日", "")
                row[0] = datetime.strptime(date_string, '%Y-%m-%d')
                row[1] = ", ".join(map(str, row[1]))  # 更改 'Room Name' 列的格式

                # 解析价格
                price_match = re.search(price_pattern, row[2])
                if price_match:
                    price = float(price_match.group(0).replace(",", ""))
                else:
                    price = None
                row[2] = price

                data.append(row)

# 将数据插入到 SQLite 数据库
for row in data:
    check_in = row[0].strftime('%Y-%m-%d')
    room_name = row[1]
    price = row[2]
    status = row[3]

    c.execute("INSERT INTO hotel VALUES (?, ?, ?, ?)", (check_in, room_name, price, status))

# 提交更改并关闭连接
conn.commit()
conn.close()

# 打印 SQLite 数据库文件路径
print(f"SQLite database file path: {db_path}")

# 连接到数据库文件
conn = sqlite3.connect('results.db')
c = conn.cursor()

# 查询 hotel 表格中的所有数据
c.execute("SELECT * FROM hotel")
rows = c.fetchall()
for row in rows:
    print(row)

# 关闭连接
conn.close()