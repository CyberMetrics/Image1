# 📡 R.A.D.A.R - Real-time Anomaly Detection & Response

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**RADAR** is a next-generation security monitoring tool that uses **Autoencoders (Deep Learning)** to detect anomalies in system logs in real-time.

---

## 🏗️ Architecture

The system is built as a **Microservices Architecture**:

| Service | Badge | Description | Port |
| :--- | :--- | :--- | :--- |
| **Web Service** | `services/web` | Flask UI, Dashboard, and MongoDB Connector | `5000` |
| **ML Service** | `services/ml` | PyTorch Autoencoder Inference Engine | `5001` |

---

## 🚀 Quick Start (No Docker Required)

If you just want to run the app immediately without installing extra tools:

### Prerequisites
-   **Python 3.9+**
-   **MongoDB URI** (Pre-configured in `config/settings.py`)

### Run the Script
We have included a helper script that installs dependencies and launches both services.

```powershell
.\run_locally.ps1
```

> **Note:** Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🐳 Run with Docker (Recommended)
For a production-grade, isolated environment.

1.  **[Install Docker Desktop](https://www.docker.com/products/docker-desktop/)**
2.  Run the composition:

```bash
docker-compose up --build
```
The services will orchestrate automatically.

---

## ☁️ Deployment

### Render.com (Free Tier)
This project is configured for **Render**.
1.  Connect your GitHub repository.
2.  Create **Web Services** for `radar-ml` and `radar-web`.
3.  See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step free tier instructions.

---

### 🛠️ Tech Stack
-   **Backend:** Flask, Python
-   **ML Engine:** PyTorch, Scikit-Learn, Sentence-Transformers
-   **Database:** MongoDB Atlas (Cloud)
-   **Frontend:** HTML5, CSS3, Vanilla JS (Dark Mode Optimized)

---
*Created by CyberMetrics*
