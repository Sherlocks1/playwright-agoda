import pymongo

# 数据库连接信息
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'hotel'
MONGO_COLLECTION = 'booking'

# 数据库客户端和集合对象
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]
collection = db[MONGO_COLLECTION]

# 删除集合内的所有文档
result = collection.delete_many({})
print(result.deleted_count)