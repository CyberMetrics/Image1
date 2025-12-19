from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def get_log(offset=0):
    cursor = collection.find().sort("timestamp", 1).skip(offset).limit(1)
    docs = list(cursor)
    return docs[0] if docs else None

def get_total_logs():
    return collection.count_documents({})
