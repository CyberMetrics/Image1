import torch
import torch.nn as nn
import numpy as np
import joblib


from .preprocess import fit_vectorizer, vectorize_log

MODEL_PATH = "ml/autoencoder_model.pt"
VECTORIZER_PATH = "ml/vectorizer.joblib"

class AutoEncoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(64, 256),
            nn.ReLU(),
            nn.Linear(256, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)


def train():
    from .load_data import load_logs
    logs = load_logs(2000)

    encoder, scaler = fit_vectorizer(logs)
    joblib.dump((encoder, scaler), VECTORIZER_PATH)
    print("Vectorizer saved at →", VECTORIZER_PATH)

    X = np.array([vectorize_log(log, encoder, scaler) for log in logs])
    input_dim = X.shape[1]

    model = AutoEncoder(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.MSELoss()
    X_tensor = torch.tensor(X, dtype=torch.float32)

    for epoch in range(20):
        optimizer.zero_grad()
        out = model(X_tensor)
        loss = loss_fn(out, X_tensor)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/20 | Loss = {loss.item():.6f}")

    torch.save(model.state_dict(), MODEL_PATH)
    print("Model saved at →", MODEL_PATH)


if __name__ == "__main__":
    train()
