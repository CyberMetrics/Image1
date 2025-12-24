FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (including ml/ and config/)
COPY . .

EXPOSE 5001

ENV MALLOC_ARENA_MAX=2
CMD sh -c "gunicorn app:app -w 1 -b 0.0.0.0:${PORT:-5001} --timeout 120"
