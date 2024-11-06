
FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx 
RUN apt-get install -y libglib2.0-0
RUN pip install torch==2.0.1
