# config/settings.py

MONGO_URI = (
    "mongodb+srv://satishpakalapati59_db_user:satish@cluster0.7salcwk.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)

MONGO_DB = "RADAR"
MONGO_COLLECTION = "Event_Logs"

MODEL_PATH = "ml/autoencoder_model.pt"
VECTORIZER_PATH = "ml/vectorizer.joblib"
