FROM python:3.8-slim-buster

ENV DB_HOST=postgres
ENV DB_USER=somu
ENV DB_PASSWORD=mypwd
ENV DB_NAME=mockdb
ENV DB_PORT=5432

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y libpq-dev libssl-dev libffi-dev gcc g++
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["python", "server.py"]