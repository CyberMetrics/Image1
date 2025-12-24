from pymongo import MongoClient
import os
import sys

# Setup paths (hacky but works for script)
sys.path.append(os.path.join(os.getcwd(), 'services', 'web'))
from config.settings import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

print(f"Connected to DB: {MONGO_DB}")
print("-" * 30)

cols = db.list_collection_names()
print(f"Total Collections: {len(cols)}")
print("Collections found:")
for c in cols:
    count = db[c].count_documents({})
    print(f" - {c}: {count} docs")

print("-" * 30)
print("Done.")
