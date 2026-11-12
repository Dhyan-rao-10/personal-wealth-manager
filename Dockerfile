FROM python:3.12-slim

# Links the published image to this repository, which lets the CD workflow create the package.
LABEL org.opencontainers.image.source="https://github.com/Dhyan-rao-10/personal-wealth-manager"
LABEL org.opencontainers.image.description="Personal Wealth Manager - SE mini-project, Team 5"

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# The database lives in /data, so mount a volume there to keep it between runs.
ENV DATABASE_URL=sqlite:////data/wealth.db
RUN useradd --system appuser && mkdir /data && chown appuser /data
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
