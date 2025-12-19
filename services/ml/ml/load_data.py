from database.mongo import collection

def load_logs(limit=2000):
    """
    Load logs from MongoDB for ML training.
    """
    cursor = collection.find().sort("timestamp", 1).limit(limit)
    return list(cursor)
