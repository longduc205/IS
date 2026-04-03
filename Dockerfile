FROM python:3.11-slim

RUN groupadd -r vulnlab && useradd -r -g vulnlab vulnlab

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/app/static/uploads && \
    chown -R vulnlab:vulnlab /app

USER vulnlab

EXPOSE 5000

CMD ["python", "run.py"]
