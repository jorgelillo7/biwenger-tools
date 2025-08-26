FROM python:3.9-slim

WORKDIR /app

COPY scraper-job/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY scraper-job/ ./scraper-job/

WORKDIR /app/scraper-job

ENV PYTHONPATH=/app
CMD ["python", "-m", "scraper-job.get_messages"]
