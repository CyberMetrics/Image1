FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["gunicorn", "app:app", "-w", "1", "-b", "0.0.0.0:5002", "--timeout", "120"]
