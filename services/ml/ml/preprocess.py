import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler



# Global cache for the embedder
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        # Lazy load only when needed
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# Map text log levels → numbers
LEVEL_MAP = {
    "info": 1,
    "information": 1,
    "warn": 2,
    "warning": 2,
    "error": 3,
    "critical": 4,
    "fatal": 5
}

def normalize_level(level):
    """
    Convert level to integer (robust)
    """
    if isinstance(level, int):
        return level

    if isinstance(level, str):
        clean = level.strip().lower()

        # numeric string
        if clean.isdigit():
            return int(clean)

        # text category
        if clean in LEVEL_MAP:
            return LEVEL_MAP[clean]

    # fallback
    return 1


def fit_vectorizer(logs):
    sources = np.array([log.get("source", "") for log in logs]).reshape(-1, 1)
    os_types = np.array([log.get("os_type", "") for log in logs]).reshape(-1, 1)

    encoder = OneHotEncoder(handle_unknown="ignore")
    encoder.fit(np.hstack([sources, os_types]))

    # Normalize all levels
    levels = np.array([[normalize_level(log.get("level"))] for log in logs])

    scaler = MinMaxScaler()
    scaler.fit(levels)

    return encoder, scaler


def vectorize_log(log, encoder, scaler):
    msg = log.get("message", "")
    
    # Use lazy loader
    embedder = get_embedder()
    msg_emb = embedder.encode(msg)

    src = log.get("source", "")
    ost = log.get("os_type", "")

    cat_vec = encoder.transform([[src, ost]]).toarray()[0]

    lvl_norm = normalize_level(log.get("level"))
    lvl = scaler.transform([[lvl_norm]])[0]

    return np.hstack([msg_emb, cat_vec, lvl])
