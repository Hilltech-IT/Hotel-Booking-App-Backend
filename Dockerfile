# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.10.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV CURRENT_ENVIRONMENT=DEVELOPMENT
ENV BROKER_URL=amqp://guest:guest@34.16.123.89:5672
ENV DEFAULT_FRONTENT_URL=http://34.171.61.167:3000
ENV DEFAULT_BACKEND_URL=http://34.171.61.167:8000

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001


RUN apt-get update && \
    apt-get install -y sudo && \
    rm -rf /var/lib/apt/lists/*
# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
#USER root

# Copy the source code into the container.
#COPY . .
COPY --chown=user:group . .
RUN sudo chmod 777 celerybeat-schedule.db
RUN python manage.py collectstatic 

# Migrations
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD gunicorn 'HotelBookingBackend.wsgi' --bind=0.0.0.0:8000 --workers=3
#CMD ["gunicorn", "InfluencerMarketer.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
