FROM python:3.8-slim-buster
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev libssl-dev libffi-dev gcc g++
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "server.py"]