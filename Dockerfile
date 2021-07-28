FROM python:3.7.0

WORKDIR usr/src/flask_app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# To disable the Python stdout buffering, you can to set the user environment variable
# PYTHONUNBUFFERED keeps Python from buffering our standard
ENV PYTHONUNBUFFERED=TRUE
