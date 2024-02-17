# pull official base image
FROM python:3.11.2-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update and upgrade apt packages
RUN apt-get update -y && apt-get upgrade -y

RUN apt-get update && apt-get install -y \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 apt-utils \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 libgtk-3-0 libxtst6\
    curl unzip wget figlet iputils-ping\
    xvfb


# Clean up
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# install dependencies
RUN pip install --upgrade pip
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./compose/backend/start /start-fastapi
RUN sed -i 's/\r$//g' /start-fastapi
RUN chmod +x /start-fastapi

COPY ./compose/aiogram/start /start-aiogram
RUN sed -i 's/\r$//g' /start-aiogram
RUN chmod +x /start-aiogram

COPY ./compose/scheduler/start /start-scheduler
RUN sed -i 's/\r$//g' /start-scheduler
RUN chmod +x /start-scheduler

# set work directory
WORKDIR /app
