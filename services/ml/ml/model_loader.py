import torch
import numpy as np
import joblib

from ml.preprocess import vectorize_log
from ml.train_autoencoder import AutoEncoder
from config.settings import VECTORIZER_PATH

MODEL_PATH = "ml/autoencoder_model.pt"

# Load vectorizer
encoder, scaler = joblib.load(VECTORIZER_PATH)


def load_model(input_dim):
    """
    Load PyTorch Autoencoder model with correct input dimension.
    """
    model = AutoEncoder(input_dim)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
    model.eval()
    return model


def compute_score(log):
    """
    Compute anomaly score using reconstruction error.
    """
    vec = vectorize_log(log, encoder, scaler)
    input_dim = len(vec)

    model = load_model(input_dim)

    x = torch.tensor(vec, dtype=torch.float32)
    out = model(x)

    mse = torch.mean((x - out) ** 2).item()
    return round(mse, 6)
