from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def get_log(offset=0, target_col=None):
    if target_col is None:
        target_col = collection
    cursor = target_col.find().sort("timestamp", 1).skip(offset).limit(1)
    docs = list(cursor)
    return docs[0] if docs else None

def get_logs(skip=0, limit=20, target_col=None, query=None):
    if target_col is None:
        target_col = collection
    if query is None:
        query = {}
    
    # Sort by timestamp ascending (or _id asc) so graph draws left-to-right correctly
    cursor = target_col.find(query).sort("timestamp", 1).skip(skip).limit(limit)
    return list(cursor)

def get_total_logs(target_col=None):
    if target_col is None:
        target_col = collection
    return target_col.count_documents({})

def find_user_collection(username):
    """
    Finds strict match for user collection.
    User requirement: Collection name is exactly the username (email).
    """
    if not username:
        return None
    
    # Refresh/Caching might be needed in high scale, but for now list_collection_names is fine
    collections = db.list_collection_names()
    if username in collections:
        return username
    return None
