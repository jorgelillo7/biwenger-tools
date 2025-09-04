FROM python:3.9-slim

WORKDIR /app

COPY scraper_job/requirements.txt ./scraper_job/
COPY core/requirements.txt ./core/

RUN pip install --no-cache-dir -r scraper_job/requirements.txt
RUN pip install --no-cache-dir -r core/requirements.txt

COPY core/ ./core/
COPY scraper_job/ ./scraper_job/

WORKDIR /app/scraper_job

ENV PYTHONPATH=/app
CMD ["python", "-m", "scraper_job.get_messages"]
